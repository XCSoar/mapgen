import os, sys
import shutil
import cherrypy
import shelve
import time
import traceback
import fcntl
from genshi.filters import HTMLFormFiller
from xcsoar.mapgen.job import Job
from xcsoar.mapgen import view
from xcsoar.mapgen.georect import GeoRect
from xcsoar.mapgen.waypoint import WaypointList

class Server(object):
    def __init__(self, dir_jobs):
        self.__dir_jobs = os.path.abspath(dir_jobs)

    def too_many_requests(self):
        db = None
        lock = None
        try:
            if not os.path.exists(self.__dir_jobs):
                os.makedirs(self.__dir_jobs)
            lock = open(os.path.join(self.__dir_jobs, 'requests.db.lock'), 'a')
            fcntl.flock(lock, fcntl.LOCK_EX)
            db = shelve.open(os.path.join(self.__dir_jobs, 'requests.db'))
            for ip in db.keys():
                times = db[ip]
                for t in times:
                    if time.time() - t > 3600:
                        times.remove(t)
                if len(times) == 0:
                    db.remove(ip)
                else:
                    db[ip] = times
            ip = cherrypy.request.remote.ip
            if db.has_key(ip):
                if len(db[ip]) >= 3:
                    return True
                times = db[ip]
                times.append(int(time.time()))
                db[ip] = times
            else:
                db[ip] = [int(time.time())]
            return False
        except Exception, e:
            print 'Error: ' + str(e)
            traceback.print_exc(file=sys.stdout)
            return False
        finally:
            if lock != None:
                lock.close()
            if db != None:
                db.close()

    @cherrypy.expose
    @view.output('index.html')
    def index(self):
        return view.render()

    @cherrypy.expose
    @view.output('index.html')
    def generate(self, name, mail, waypoint_file, left, right, top, bottom):
        filler = HTMLFormFiller(data=dict(name=name, mail=mail, left=left, right=right, top=top, bottom=bottom))

        name = name.strip()
        if name == "":
            return view.render(error='No map name given!') | filler

        if not waypoint_file.file:
            return view.render(error='Waypoint file could not be read!') | filler

        job = Job(self.__dir_jobs)
        desc = job.description
        desc.name = name
        desc.mail = mail
        desc.waypoint_file = 'waypoints.dat'

        try:
            desc.bounds = GeoRect(float(left.strip()), float(right.strip()), float(top.strip()), float(bottom.strip()))
        except:
            pass

        waypoint_path = job.file_path(desc.waypoint_file)
        f = open(waypoint_path, "w")
        shutil.copyfileobj(fsrc=waypoint_file.file, fdst=f, length=1024 * 64)
        f.close()

        if os.path.getsize(waypoint_path) == 0:
            os.unlink(waypoint_path)
            desc.waypoint_file = None

        if desc.bounds == None:
            if desc.waypoint_file == None:
                job.delete()
                return view.render(error='Waypoint file or bounds are required!') | filler
            desc.bounds = WaypointList().parse_file(waypoint_path).get_bounds()

        if desc.bounds.height() > 90 or desc.bounds.width() > 90:
            return view.render(error='Selected area is too large.') | filler

        if self.too_many_requests():
            job.delete()
            return view.render(error='You can generate only three maps per hour.') | filler

        job.enqueue()
        raise cherrypy.HTTPRedirect(cherrypy.url('/status?uuid=' + job.uuid))

    @cherrypy.expose
    @view.output('status.html')
    def status(self, uuid):
        job = Job.find(self.__dir_jobs, uuid)
        if job == None:
            return view.render('error.html', error='Job not found!')
        status = job.status()
        if status == 'Error':
            return view.render('error.html', error='Generation failed!')
        elif status == 'Done':
            return view.render('done.html', name=job.description.name, uuid=uuid)
        return view.render(uuid=uuid, name=job.description.name, status=status)

    @cherrypy.expose
    def download(self, uuid):
        job = Job.find(self.__dir_jobs, uuid)
        if not job or job.status() != 'Done':
            return self.status(uuid)
        return cherrypy.lib.static.serve_download(job.map_file(), job.description.name + '.xcm')
