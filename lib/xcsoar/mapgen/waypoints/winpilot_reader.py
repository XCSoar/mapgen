# -*- coding: utf-8 -*-
from xcsoar.mapgen.waypoints.waypoint import Waypoint
from xcsoar.mapgen.waypoints.list import WaypointList


def __parse_altitude(str):
    str = str.lower()
    if str.endswith("ft") or str.endswith("f"):
        str = str.rstrip("ft")
        return int(str) * 0.3048
    else:
        str = str.rstrip("m")
        float_alt = float(str)
        int_alt = int(float_alt)

    return int(int_alt)


# Winpilot .DAT file lat/lon formats
# Latitude, Longitude: in one of the following formats (ss=seconds, dd = decimals):
# dd:mm:ss (for example: 36:15:20N)
# dd:mm.d (for example: 36:15.3N)
# dd:mm.dd (for example: 36:15.33N)
# dd:mm.ddd (for example: 36:15.333N)
def __parse_coordinate(str):

    str = str.lower()
    negative = str.endswith("s") or str.endswith("w")
    str = str.rstrip("sw") if negative else str.rstrip("ne")

    strsplit = str.split(":")
    if len(strsplit) < 2:
        return None

    if len(strsplit) == 2:
        # degrees + minutes / 60
        a = int(strsplit[0]) + float(strsplit[1]) / 60

    if len(strsplit) == 3:
        # degrees + minutes / 60 + seconds / 3600
        a = int(str[0]) + float(str[1]) / 60 + float(str[2]) / 3600

    if negative:
        a *= -1

    return a


def parse_winpilot_waypoints(lines):

    waypoint_list = WaypointList()
    wpnum = 0
    for byteline in lines:
        wpnum += 1

        line = byteline.decode("UTF-8")
        line = line.strip()
        if line == "" or line.startswith("*"):
            continue

        fields = line.split(",")
        if len(fields) < 6:
            continue

        wp = Waypoint()
        wp.lat = __parse_coordinate(fields[1])
        wp.lon = __parse_coordinate(fields[2])
        wp.altitude = __parse_altitude(fields[3])
        wp.name = fields[5].strip()

        waypoint_list.append(wp)

    return waypoint_list
