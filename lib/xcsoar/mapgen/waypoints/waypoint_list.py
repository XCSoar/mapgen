from xcsoar.mapgen.waypoints.waypoint import Waypoint
from xcsoar.mapgen.waypoints.seeyou import parse_seeyou_waypoints
from xcsoar.mapgen.waypoints.winpilot import parse_winpilot_waypoints
from xcsoar.mapgen.georect import GeoRect
from xcsoar.mapgen.geopoint import GeoPoint

class WaypointList:
    def __init__(self):
        self.__list = []

    def __len__(self):
        return len(self.__list)

    def __getitem__(self, i):
        if i < 0 or i > len(self):
            return None
        return self.__list[i]

    def __iter__(self):
        return iter(self.__list)

    def append(self, wp):
        self.__list.append(wp)

    def extend(self, wp_list):
        self.__list.extend(wp_list)

    def get_bounds(self, distance = 15.):
        rc = GeoRect(180, -180, -90, 90)
        for wp in self.__list:
            rc.left = min(rc.left, wp.lon)
            rc.right = max(rc.right, wp.lon)
            rc.top = max(rc.top, wp.lat)
            rc.bottom = min(rc.bottom, wp.lat)
        
        rc.expand(distance)
        return rc

    def parse_file(self, filename):
        f = open(filename, 'r')
        try:
            return self.parse(f, filename)
        finally:
            f.close()

    def parse(self, lines, filename = 'unknown.dat'):
        if filename.lower().endswith('.xcw') or filename.lower().endswith('.dat'):
            self.extend(parse_winpilot_waypoints(lines))
        elif filename.lower().endswith('.cup'):
            self.extend(parse_seeyou_waypoints(lines))
        else:
            raise RuntimeError('Waypoint file {} has an unsupported format.'.format(filename))
        
        return self
