from xcsoar.mapgen.waypoints.list import WaypointList

def __compose_line(waypoint):
    # "Aachen Merzbruc",AACHE,DE,5049.383N,00611.183E,189.0m,5,80,530.0m,"122.875",
    str = '"' + waypoint.name + '",'
    str += waypoint.short_name + ','
    str += waypoint.country_code + ','

    lat = abs(waypoint.lat)
    str += "{:02d}".format(int(lat))
    lat = round((lat - int(lat)) * 60, 3)
    str += "{:06.3f}".format(lat)
    str += 'N,' if waypoint.lat > 0 else 'S,'
    lon = abs(waypoint.lon)
    str += "{:03d}".format(int(lon))
    lon = round((lon - int(lon)) * 60, 3)
    str += "{:06.3f}".format(lon)
    str += 'E,' if waypoint.lon > 0 else 'W,'
    if waypoint.altitude and waypoint.altitude > -500:
        str += "{:.1f}m,".format(waypoint.altitude)
    else: str += ","

    if waypoint.cup_type:
        str += "{:d},".format(waypoint.cup_type)
    elif waypoint.type:
        if waypoint.type == 'ulm':
            if waypoint.runway_len and waypoint.runway_len > 500:
                waypoint.type = 'airport'
            else:
                waypoint.type = 'outlanding'

        if waypoint.type == 'outlanding': str += "3,"
        elif waypoint.type == 'glider_site': str += "4,"
        elif waypoint.type == 'airport': 
            if waypoint.surface and waypoint.surface in [
                'concrete',
                'asphalt',
            ]: 
                str += "5,"
            else: 
                str += "2,"
        elif waypoint.type == 'mountain pass': str += "6,"
        elif waypoint.type == 'mountain top': str += "7,"
        elif waypoint.type == 'tower': str += "8,"
        elif waypoint.type == 'tunnel': str += "13,"
        elif waypoint.type == 'bridge': str += "14,"
        elif waypoint.type == 'powerplant': str += "15,"
        elif waypoint.type == 'castle': str += "16,"
        elif waypoint.type.endswith('junction'): str += "17,"
        elif waypoint.type.endswith('cross'): str += "17,"
        else: str += "1,"
    else: str += "1,"

    if waypoint.runway_dir:
        str += "{:03d}".format(waypoint.runway_dir)

    str += ','
    if waypoint.runway_len:
        str += "{:03d}.0m".format(waypoint.runway_len)

    str += ','
    if waypoint.freq:
        str += "{:07.3f}".format(waypoint.freq)

    str += ','
    if waypoint.comment:
        str += '"' + waypoint.comment + '"'

    return str

def write_seeyou_waypoints(waypoints, path):
    if not isinstance(waypoints, WaypointList): 
        raise TypeError("WaypointList expected")
    
    with open(path, "w") as f:
        for waypoint in waypoints:
            f.write(__compose_line(waypoint) + '\r\n')
    
    return path
