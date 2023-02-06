#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

app_dir = os.path.abspath(__file__ + "/../..")
sys.path.append(os.path.join(app_dir, "lib"))

import cherrypy
from flup.server.fcgi import WSGIServer
from xcsoar.mapgen.server.server import Server

cherrypy.config.update(
    {"tools.encode.on": True, "tools.encode.encoding": "UTF-8", "tools.decode.on": True}
)

app = cherrypy.tree.mount(Server(dir_jobs=os.path.join(app_dir, "jobs")), "/mapgen")
cherrypy.engine.start(blocking=False)

try:
    WSGIServer(app).run()
finally:
    # This ensures that any left-over threads are stopped as well.
    cherrypy.engine.stop()
