from xcsoar.mapgen.geopoint import GeoPoint

class Waypoint(GeoPoint):
    def __init__(self):
        self.altitude = 0
        self.name = ''

    def __str__(self):
        return '{}, {}, {}'.format(self.name, super(), self.altitude)

