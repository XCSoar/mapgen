# -*- coding: utf-8 -*-
import pickle
import time
import os
import shutil
import uuid

from xcsoar.mapgen.util import slurp, spew


class JobDescription:
    name = None
    mail = None
    waypoint_file = None
    waypoint_details_file = None
    airspace_file = None
    use_topology = True
    use_terrain = True
    bounds = None
    resolution = 9.0
    download_url = None
    compressed = False
    level_of_detail = 3
    welt2000 = False


class Job:
    def __init__(self, dir_jobs, desc=None):
        if desc:
            self.uuid = self.__generate_uuid()
            self.dir = os.path.join(dir_jobs, self.uuid + ".locked")
            self.description = desc
            if not os.path.exists(self.dir):
                os.makedirs(self.dir)
                spew(os.path.join(self.dir, "timestamp"), time.time())
        else:
            self.dir = dir_jobs
            self.uuid = os.path.basename(self.dir).split(".")[0]
            f = open(self.__job_file(), "rb")
            try:
                self.description = pickle.load(f)
            finally:
                f.close()

    def enqueue(self):
        f = open(self.__job_file(), "wb")
        try:
            pickle.dump(self.description, f)
        finally:
            f.close()
        self.__move(".queued")

    def file_path(self, name):
        return os.path.join(self.dir, name)

    def map_file(self):
        return self.file_path("map.xcm")

    def __status_file(self):
        return self.file_path("status")

    def __job_file(self):
        return self.file_path("job")

    def error(self):
        self.__move(".error")
        try:
            os.unlink(self.__status_file())
        except:
            pass

    def done(self):
        self.__move()
        os.unlink(self.__status_file())

    def update_status(self, status):
        spew(self.__status_file(), status)

    def delete(self):
        shutil.rmtree(self.dir)

    def status(self):
        path = self.__status_file()
        if os.path.exists(path):
            return slurp(path)
        name = os.path.basename(self.dir)
        i = name.find(".")
        if i == -1:
            return "Done"
        return name[i + 1 :].capitalize()

    def __move(self, postfix=""):
        old = self.dir
        self.dir = os.path.join(os.path.dirname(old), self.uuid + postfix)
        os.rename(old, self.dir)

    def __generate_uuid(self):
        return str(uuid.uuid1())

    @staticmethod
    def find(dir_jobs, uuid):
        base = os.path.join(dir_jobs, uuid)
        for suffix in ["", ".locked", ".queued", ".working", ".error"]:
            if os.path.exists(base + suffix):
                return Job(base + suffix)

        return None

    @staticmethod
    def get_next(dir_jobs):
        if not os.path.exists(dir_jobs):
            return None

        next_dir = None
        next_ts = time.time()
        for entry in os.listdir(dir_jobs):
            dir = os.path.join(dir_jobs, entry)

            # Only directories can be jobs
            if not os.path.isdir(dir):
                continue

            ts = None
            try:
                ts = float(slurp(os.path.join(dir, "timestamp")))
            except Exception as e:
                print(("Could not read timestamp file for job {}\n{}".format(dir, e)))
                continue

            age = time.time() - ts

            # Check if there is a running job which is expired
            if (
                (dir.endswith(".locked") or dir.endswith(".working"))
            ) and age > 60**2:
                print(("Delete expired job {}".format(dir)))
                shutil.rmtree(dir)
                continue

            # Find an enqueued job
            if dir.endswith(".queued"):
                if ts < next_ts:
                    next_dir = dir
                    next_ts = ts
            elif age > 24 * 7 * 60 * 60:
                # Delete if download is expired
                print(("Delete expired job {}".format(dir)))
                shutil.rmtree(dir)

        if next_dir != None:
            job = Job(next_dir)
            job.__move(".working")
            return job
        return None
