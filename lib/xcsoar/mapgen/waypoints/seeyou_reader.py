# -*- coding: utf-8 -*-
from xcsoar.mapgen.waypoints.waypoint import Waypoint
from xcsoar.mapgen.waypoints.list import WaypointList


class __CSVLine:
    def __init__(self, line):
        self.__line = line
        self.__index = 0

    def has_next(self):
        return self.__index < len(self.__line)

    def __next__(self):
        if self.__index >= len(self.__line):
            return None

        in_quotes = False

        for i in range(self.__index, len(self.__line)):
            if self.__line[i] == '"':
                in_quotes = not in_quotes

            if self.__line[i] == "," and not in_quotes:
                break

        next = (
            self.__line[self.__index : i + 1].rstrip(",").strip('"').replace('"', '"')
        )
        self.__index = i + 1

        return next

    next = __next__


def __parse_altitude(str):
    str = str.lower()
    if str.endswith("ft") or str.endswith("f"):
        str = str.rstrip("ft")
        return int(float(str) * 0.3048)
    else:
        str = str.rstrip("m")
        if len(str) > 0:
            return int(float(str))
        else:
            return None


def __parse_coordinate(str):
    str = str.lower()
    negative = str.endswith("s") or str.endswith("w")
    is_lon = str.endswith("e") or str.endswith("w")
    str = str.rstrip("sw") if negative else str.rstrip("ne")

    # degrees + minutes / 60
    if is_lon:
        a = int(str[:3]) + float(str[3:]) / 60
    else:
        a = int(str[:2]) + float(str[2:]) / 60

    if negative:
        a *= -1
    return a


def __parse_length(str):
    str = str.lower()
    if str.endswith("m"):
        str = str.rstrip("m")
        return int(float(str))
    else:
        return None


def parse_seeyou_waypoints(lines, bounds=None):
    waypoint_list = WaypointList()

    header = None
    columns = {}

    for raw_line in lines:
        if isinstance(raw_line, bytes):
            try:
                line = raw_line.decode("utf-8")
            except UnicodeDecodeError:
                line = raw_line.decode("windows-1252")
            line = line.strip()
        else:
            line = raw_line.strip()

        if not line or line.startswith("*"):
            continue

        if line == "-----Related Tasks-----":
            break

        # Parse CSV
        fields = []
        csv_line = __CSVLine(line)
        while csv_line.has_next():
            fields.append(next(csv_line))

        # First non-comment line is the header
        if header is None:
            header = [f.strip().lower() for f in fields]
            columns = {name: idx for idx, name in enumerate(header)}
            continue

        def get(name, default=""):
            idx = columns.get(name)
            if idx is None or idx >= len(fields):
                return default
            return fields[idx]

        try:
            lat = __parse_coordinate(get("lat"))
            lon = __parse_coordinate(get("lon"))
        except Exception:
            continue

        if bounds:
            if lat > bounds.top or lat < bounds.bottom:
                continue
            if lon > bounds.right or lon < bounds.left:
                continue

        wp = Waypoint()
        wp.lat = lat
        wp.lon = lon

        wp.name = get("name").strip()
        wp.country_code = get("country").strip()

        elev = get("elev")
        if elev:
            wp.altitude = __parse_altitude(elev)

        style = get("style")
        if style:
            wp.cup_type = int(style)

        rwdir = get("rwdir")
        if rwdir:
            wp.runway_dir = int(rwdir)

        rwlen = get("rwlen")
        if rwlen:
            wp.runway_len = __parse_length(rwlen)

        freq = get("freq")
        if freq:
            wp.freq = float(freq)

        desc = get("desc")
        if desc:
            wp.comment = desc.strip()

        waypoint_list.append(wp)

    return waypoint_list
