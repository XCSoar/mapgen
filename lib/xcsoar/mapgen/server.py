import os, sys
import shutil
import cherrypy
import shelve
import time
import traceback
import fcntl
from genshi.filters import HTMLFormFiller
from xcsoar.mapgen.job import Job, JobDescription
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
                    del db[ip]
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
    def index(self, **params):
        if cherrypy.request.method != 'POST':
            return view.render()

        name = params['name'].strip()
        if name == "":
            return view.render(error='No map name given!') | HTMLFormFiller(data=params)

        desc = JobDescription()
        desc.name = name
        desc.mail = params['mail']
        desc.resolution = 3.0 if params.has_key('highres') else 9.0

        selection = params['selection']
        waypoint_file = params['waypoint_file']
        if selection == 'waypoint' or selection == 'waypoint_bounds':
            if not waypoint_file.file or not waypoint_file.filename:
                return view.render(error='No waypoint file uploaded.') | HTMLFormFiller(data=params)

            try:
                desc.bounds = WaypointList().parse(waypoint_file.file, waypoint_file.filename).get_bounds()
                desc.waypoint_file = 'waypoints.dat'
            except:
                return view.render(error='Unsupported waypoint file ' + waypoint_file.filename) | HTMLFormFiller(data=params)

        if selection == 'bounds' or selection == 'waypoint_bounds':
            try:
                desc.bounds = GeoRect(float(params['left']),
                                      float(params['right']),
                                      float(params['top']),
                                      float(params['bottom']))
            except:
                return view.render(error='Map bounds not set.') | HTMLFormFiller(data=params)

        if desc.bounds.height() <= 0 or desc.bounds.width() <= 0:
            return view.render(error='Bounds are invalid.') | HTMLFormFiller(data=params)

        if desc.bounds.height() * desc.bounds.width() > 1000:
            return view.render(error='Selected area is too large.') | HTMLFormFiller(data=params)

        if self.too_many_requests():
            return view.render(error='You can generate only three maps per hour.') | HTMLFormFiller(data=params)

        job = Job(self.__dir_jobs, desc)

        if desc.waypoint_file:
            f = open(job.file_path(desc.waypoint_file), 'w')
            waypoint_file.file.seek(0)
            shutil.copyfileobj(fsrc=waypoint_file.file, fdst=f, length=1024 * 64)
            f.close()

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
