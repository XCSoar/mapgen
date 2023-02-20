# -*- coding: utf-8 -*-
import subprocess, sys


def slurp(file):
    f = open(file, "r")
    try:
        return f.read()
    finally:
        f.close()


def spew(file, content):
    f = open(file, "w")
    try:
        f.write(str(content))
    finally:
        f.close()


__used_commands = {
    "ogr2ogr": "Please install gdal (https://gdal.org/).",
    "shptree": "Please install it from the mapserver package (https://mapserver.org/).",
    "7zr": "Please install 7-zip (https://7-zip.org/).",
    "wget": "Please install it using your distribution package manager.",
    "gdalwarp": "Please install gdal (https://gdal.org/).",
}


def check_commands():
    ret = True
    for cmd, help in list(__used_commands.items()):
        try:
            subprocess.check_output(["which", cmd], stderr=subprocess.STDOUT)
        except:
            ret = False
            print(("Command {} is missing on the $PATH. ".format(cmd) + help))
    if not ret:
        sys.exit(1)
