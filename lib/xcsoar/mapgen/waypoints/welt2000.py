import os
import re

from xcsoar.mapgen.georect import GeoRect
from xcsoar.mapgen.filelist import FileList

def __get_database_file(downloader, dir_data):
    path = os.path.join(dir_data, 'welt2000', 'WELT2000.TXT')

    if not os.path.exists(path):
        downloader.retrieve_extracted('welt2000/WELT2000.7z')
        
    if not os.path.exists(path):        
        raise RuntimeError('Welt2000 database not found at {}'.format(path))
    
    return path

def __parse_line(line, bounds):
    if line.startswith('$'): return None
    
    lat = line[45:52]
    lat_neg = lat.startswith('S')  
    lat = float(lat[1:3]) + float(lat[3:5]) / 60. + float(lat[5:7]) / 3600.
    if lat_neg: lat = -lat
    
    if lat > bounds.top or lat < bounds.bottom: return None

    lon = line[52:60]
    lon_neg = lon.startswith('W')  
    lon = float(lon[1:4]) + float(lon[4:6]) / 60. + float(lon[6:8]) / 3600.
    if lon_neg: lon = -lon
    
    if lon > bounds.right or lon < bounds.left: return None
    
    wp = {'lat': lat, 'lon': lon}

    elev = line[41:45].strip()
    if elev != '': wp['elev'] = float(elev)
    else: wp['elev'] = 0.0

    wp['shortname'] = line[:6]
    if wp['shortname'].endswith('1'): wp['airport'] = True
    if wp['shortname'].endswith('2'): wp['outlanding'] = True
    
    wp['shortname'] = wp['shortname'].strip()
    
    wp['name'] = line[7:41].strip()
    
    if 'GLD' in wp['name']: wp['glider_site'] = True
    if 'ULM' in wp['name']: wp['ulm'] = True
    
    pos = -1
    if '#' in wp['name']: pos = wp['name'].find('#')
    if '*' in wp['name']: pos = wp['name'].find('*')
        
    if pos > -1:        
        data = wp['name'][pos + 1:]
        wp['name'] = wp['name'][:pos].strip()
        
        icao = data[:4]
        if not icao.startswith('GLD') and not icao.startswith('ULM'): wp['icoa'] = icao
        
        if data[4:5] == 'A': wp['surface'] = 'asphalt'
        elif data[4:5] == 'C': wp['surface'] = 'concrete'
        elif data[4:5] == 'L': wp['surface'] = 'loam'
        elif data[4:5] == 'S': wp['surface'] = 'sand'
        elif data[4:5] == 'Y': wp['surface'] = 'clay'
        elif data[4:5] == 'G': wp['surface'] = 'gras'
        elif data[4:5] == 'V': wp['surface'] = 'gravel'
        elif data[4:5] == 'D': wp['surface'] = 'dirt'

        runway_len = data[5:8].strip()
        if runway_len != '':
            wp['runway_len'] = int(runway_len) * 10
        
        runway_dir = data[8:10].strip()
        if runway_dir != '':
            wp['runway_dir'] = int(runway_dir) * 10
        
        freq = data[12:17].strip()
        if len(freq) == 5:
            if freq.endswith('2') or freq.endswith('7'): freq += '5'
            else: freq += '0'
            wp['freq'] = float(freq) / 1000.
    
    if wp['name'].endswith('GLD'):
        wp['name'] = wp['name'][:-3].strip()
    else:
        wp['name'] = wp['name'].rstrip('!?1 ')
    
    if re.search('(^|\s)BERG($|\s)', wp['name']): wp['type'] = 'mountain top'
    if re.search('(^|\s)COL($|\s)', wp['name']): wp['type'] = 'mountain pass'
    if re.search('(^|\s)PASS($|\s)', wp['name']): wp['type'] = 'mountain pass'
    if re.search('(^|\s)TOP($|\s)', wp['name']): wp['type'] = 'mountain top'
    if re.search('(\s)A(\d){0,3}($|\s)', wp['name']): wp['type'] = 'highway exit'
    if re.search('(\s)AB(\d){0,3}($|\s)', wp['name']): wp['type'] = 'highway exit'
    if re.search('(\s)BAB(\d){0,3}($|\s)', wp['name']): wp['type'] = 'highway exit'
    if re.search('(\s)(\w){0,3}XA(\d){0,3}($|\s)', wp['name']): wp['type'] = 'highway cross'
    if re.search('(\s)(\w){0,3}YA(\d){0,3}($|\s)', wp['name']): wp['type'] = 'highway junction'
    if re.search('(\s)STR($|\s)', wp['name']): wp['type'] = 'road'
    if re.search('(\s)SX($|\s)', wp['name']): wp['type'] = 'road cross'
    if re.search('(\s)SY($|\s)', wp['name']): wp['type'] = 'road junction'
    if re.search('(\s)EX($|\s)', wp['name']): wp['type'] = 'railway cross'
    if re.search('(\s)EY($|\s)', wp['name']): wp['type'] = 'railway junction'
    if re.search('(\s)TR($|\s)', wp['name']): wp['type'] = 'gas station'
    if re.search('(\s)BF($|\s)', wp['name']): wp['type'] = 'railway station'
    if re.search('(\s)RS($|\s)', wp['name']): wp['type'] = 'railway station'
    if re.search('(\s)BR($|\s)', wp['name']): wp['type'] = 'bridge'
    if re.search('(\s)TV($|\s)', wp['name']): wp['type'] = 'tower'
    if re.search('(\s)KW($|\s)', wp['name']): wp['type'] = 'powerplant'
        
    wp['name'] = wp['name'].title()
    
    while '  ' in wp['name']:
        wp['name'] = wp['name'].replace('  ', ' ')
    
    return wp

def __get_database(downloader, dir_data, bounds):
    db = []
    path = __get_database_file(downloader, dir_data)
    with open(path, "r") as f:
        for line in f:
            wp = __parse_line(line, bounds)
            if wp: 
                db.append(wp)
    
    return db

def __compose_line(waypoint):
    # "Aachen Merzbruc",AACHE,DE,5049.383N,00611.183E,189.0m,5,80,530.0m,"122.875",
    str = '"' + waypoint['name'] + '",'
    str += waypoint['shortname'] + ',,'
    
    lat = abs(waypoint['lat'])
    str += "{:02d}".format(int(lat))
    lat = round((lat - int(lat)) * 60, 3)
    str += "{:06.3f}".format(lat)
    if waypoint['lat'] > 0: str += 'N,' 
    else: str += 'S,'
    
    lon = abs(waypoint['lon'])
    str += "{:03d}".format(int(lon))
    lon = round((lon - int(lon)) * 60, 3)
    str += "{:06.3f}".format(lon)
    if waypoint['lon'] > 0: str += 'E,' 
    else: str += 'W,'
    
    elev = abs(waypoint['elev'])
    str += "{:.1f}m,".format(elev)
    
    if 'outlanding' in waypoint: str += "3,"
    elif 'glider_site' in waypoint: str += "4,"
    elif 'airport' in waypoint:
        if ('surface' in waypoint and 
            (waypoint['surface'] == 'concrete' or
             waypoint['surface'] == 'asphalt')): str += "5,"
        else: str += "2,"
    elif 'type' in waypoint:
        if waypoint['type'] == 'mountain pass': str += "6,"
        elif waypoint['type'] == 'mountain top': str += "7,"
        elif waypoint['type'] == 'tower': str += "8,"
        elif waypoint['type'] == 'tunnel': str += "13,"
        elif waypoint['type'] == 'bridge': str += "14,"
        elif waypoint['type'] == 'powerplant': str += "15,"
        elif waypoint['type'] == 'castle': str += "16,"
        elif waypoint['type'].endswith('junction'): str += "17,"
        elif waypoint['type'].endswith('cross'): str += "17,"
        else: str += "1,"
    else: str += "1,"

    if 'runway_dir' in waypoint:
        str += "{:03d}".format(waypoint['runway_dir'])
        
    str += ','
    if 'runway_len' in waypoint:
        str += "{:03d}.0m".format(waypoint['runway_len'])
        
    str += ','
    if 'freq' in waypoint:
        str += "{:07.3f}".format(waypoint['freq'])
        
    str += ','
    return str

def __create_waypoint_file(database, dir_temp):
    print("Creating waypoints.cup with {} entries...".format(len(database)))
    
    path = os.path.join(dir_temp, 'waypoints.cup')
    with open(path, "w") as f:
        for waypoint in database:
            line = __compose_line(waypoint)
            f.write(line + '\r\n')
    
    return path

def create(bounds, downloader, dir_data, dir_temp):
    database = __get_database(downloader, dir_data, bounds)
    file = __create_waypoint_file(database, dir_temp)
    
    list = FileList()
    list.add(file, True)
    return list
