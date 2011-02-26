import subprocess, sys

def slurp(file):
    f = open(file, 'r')
    try:
        return f.read()
    finally:
        f.close()

def spew(file, content):
    f = open(file, 'w')
    try:
        f.write(str(content))
    finally:
        f.close()

__used_commands = { 'ogr2ogr':   'Please install gdal (http://www.gdal.org/).',
                    'shptree':   'Please install it from the mapserver package (http://mapserver.org/).',
                    '7zr':       'Please install 7-zip (http://www.7-zip.org/).',
                    'wget':      'Please install it using your distribution package manager.',
                    'geojasper': 'Please install geojasper (http://www.dimin.net/software/geojasper/).',
                    'gdalwarp':  'Please install gdal (http://www.gdal.org/).' }

__commands_checked = False

def check_commands():
    global __commands_checked
    if __commands_checked:
        return
    __commands_checked = True
    ret = True
    for (cmd, help) in __used_commands.items():
        try:
            subprocess.check_output(['which', cmd], stderr=subprocess.STDOUT)
        except Exception as e:
            ret = False
            print('Command ' + cmd + ' is missing on the $PATH. ' + help)
    if not ret:
        sys.exit(1)
