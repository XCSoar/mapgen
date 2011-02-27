#!/usr/bin/python

import cherrypy
import sys, os
from flup.server.fcgi import WSGIServer

app_dir = os.path.abspath(__file__ + '/../..')
sys.path.append(os.path.join(app_dir, 'lib'))

from xcsoar.mapgen.server import Server

app = cherrypy.tree.mount(Server(dir_jobs=os.path.join(app_dir, 'jobs')), '/mapgen')
cherrypy.engine.start(blocking=False)

try:
    WSGIServer(app).run()
finally:
    # This ensures that any left-over threads are stopped as well.
    cherrypy.engine.stop()
