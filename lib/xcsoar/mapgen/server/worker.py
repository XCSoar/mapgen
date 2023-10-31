# -*- coding: utf-8 -*-
import os
import sys
import time
import smtplib
import traceback
import shutil
from xcsoar.mapgen.server.job import Job
from xcsoar.mapgen.generator import Generator
from xcsoar.mapgen.util import check_commands
from xcsoar.mapgen.server.config import mapgen


class Worker:
    def __init__(self, dir_jobs, dir_data, mail_server):
        check_commands()
        self.__dir_jobs = os.path.abspath(dir_jobs)
        self.__dir_data = os.path.abspath(dir_data)
        self.__mail_server = mail_server
        self.__run = False

    def __send_download_mail(self, job):
        try:
            print(("Sending download mail to {} ...".format(job.description.mail)))

            msg = """From: {mailfrom}
To: {to}
Subject: XCSoar Map Generator - Download ready ({name}.xcm)

The XCSoar Map Generator has finished your map: {name}
It can be downloaded at {protocol}://{domain}{url}
This link is valid for {retentiondays} days.
""".format(
                to=job.description.mail,
                name=job.description.name,
                protocol=mapgen["protocol"],
                domain=mapgen["domain"],
                mailfrom=mapgen["mailfrom"],
                retentiondays=mapgen["retentiondays"],
                url=job.description.download_url,
            )

            s = smtplib.SMTP(self.__mail_server)
            try:
                s.sendmail(mapgen["mailfrom"], job.description.mail, msg)
            finally:
                s.quit()
        except Exception as e:
            print(("Failed to send mail: {}".format(e)))

    def __do_job(self, job):
        try:
            print(
                (
                    "Generating map file for job uuid={}, name={}, mail={}".format(
                        job.uuid, job.description.name, job.description.mail
                    )
                )
            )
            description = job.description

            if not description.waypoint_file and not description.bounds:
                print("No waypoint file or bounds set. Aborting.")
                job.delete()
                return

            generator = Generator(self.__dir_data, job.file_path("tmp"))

            generator.set_bounds(description.bounds)
            generator.add_information_file(job.description.name, job.description.mail)

            if description.use_topology:
                job.update_status("Creating topology files...")
                generator.add_topology(
                    compressed=description.compressed,
                    level_of_detail=description.level_of_detail,
                )

            if description.use_terrain:
                job.update_status("Creating terrain files...")
                generator.add_terrain(description.resolution)

            if description.welt2000:
                job.update_status("Adding welt2000 waypoints...")
                generator.add_welt2000()
            elif description.waypoint_file:
                job.update_status("Adding waypoint file...")
                generator.add_waypoint_file(job.file_path(description.waypoint_file))

            if description.waypoint_details_file:
                job.update_status("Adding waypoint details file...")
                generator.add_waypoint_details_file(
                    job.file_path(description.waypoint_details_file)
                )

            if description.airspace_file:
                job.update_status("Adding airspace file...")
                generator.add_airspace_file(job.file_path(description.airspace_file))

            job.update_status("Creating map file...")

            try:
                generator.create(job.map_file())
            finally:
                generator.cleanup()

            shutil.rmtree(job.file_path("tmp"))
            job.done()
        except Exception as e:
            print(("Error: {}".format(e)))
            traceback.print_exc(file=sys.stdout)
            job.error()
            return

        print(("Map {} is ready for use.".format(job.map_file())))
        if job.description.mail != "":
            self.__send_download_mail(job)

    def run(self):
        self.__run = True
        print(("Monitoring {} for new jobs...".format(self.__dir_jobs)))
        while self.__run:
            try:
                job = Job.get_next(self.__dir_jobs)
                if not job:
                    time.sleep(0.5)
                    continue
                self.__do_job(job)
            except Exception as e:
                print(("Error: {}".format(e)))
                traceback.print_exc(file=sys.stdout)
