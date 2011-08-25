import os

from xcsoar.mapgen.waypoints.list import WaypointList
from xcsoar.mapgen.waypoints.welt2000_reader import parse_welt2000_waypoints
from xcsoar.mapgen.waypoints.seeyou_writer import write_seeyou_waypoints
from xcsoar.mapgen.georect import GeoRect
from xcsoar.mapgen.filelist import FileList

def __get_database_file(downloader, dir_data):
    path = os.path.join(dir_data, 'welt2000', 'WELT2000.TXT')

    if not os.path.exists(path):
        downloader.retrieve_extracted('welt2000/WELT2000.7z')
        
    if not os.path.exists(path):        
        raise RuntimeError('Welt2000 database not found at {}'.format(path))
    
    return path

def __get_database(downloader, dir_data, bounds = None):
    path = __get_database_file(downloader, dir_data)
    with open(path, "r") as f:
        return parse_welt2000_waypoints(f, bounds)

def __create_waypoint_file(database, dir_temp):
    print("Creating waypoints.cup with {} entries...".format(len(database)))
    
    path = os.path.join(dir_temp, 'waypoints.cup')
    write_seeyou_waypoints(database, path)
    return path

def create(downloader, dir_data, dir_temp, bounds = None):
    database = __get_database(downloader, dir_data, bounds)
    file = __create_waypoint_file(database, dir_temp)
    
    list = FileList()
    list.add(file, True)
    return list
