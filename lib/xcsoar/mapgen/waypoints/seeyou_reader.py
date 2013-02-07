from xcsoar.mapgen.waypoints.waypoint import Waypoint
from xcsoar.mapgen.waypoints.list import WaypointList

class __CSVLine:
    def __init__(self, line):
        self.__line = line
        self.__index = 0
        
    def has_next(self):
        return self.__index < len(self.__line)
    
    def next(self):
        if self.__index >= len(self.__line): return None
        
        in_quotes = False
        
        for i in range(self.__index, len(self.__line)):
            if self.__line[i] == '"': 
                in_quotes = not in_quotes
                
            if self.__line[i] == ',' and not in_quotes:
                break
            
        next = self.__line[self.__index:i + 1].rstrip(',').strip('"').replace('\"', '"')
        self.__index = i + 1

        return next

def __parse_altitude(str):
    str = str.lower()
    if str.endswith('ft') or str.endswith('f'):
        str = str.rstrip('ft')
        return int(float(str) * 0.3048)
    else:
        str = str.rstrip('m')
        return int(float(str))

def __parse_coordinate(str):
    str = str.lower()
    negative = str.endswith('s') or str.endswith('w')
    is_lon = str.endswith('e') or str.endswith('w')
    str = str.rstrip('sw') if negative else str.rstrip('ne')

    # degrees + minutes / 60
    if is_lon: a = int(str[:3]) + float(str[3:]) / 60
    else:      a = int(str[:2]) + float(str[2:]) / 60
        
    if (negative): a *= -1
    return a

def __parse_length(str):
    str = str.lower()
    if (str.endswith('m')):
        str = str.rstrip('m');
        return int(float(str))
    else:
        return None;

def parse_seeyou_waypoints(lines, bounds = None):
    waypoint_list = WaypointList()
    
    first = True
    for line in lines:
        if first: 
            first = False
            continue
        
        line = line.strip()
        if line == '' or line.startswith('*'):
            continue
        
        if line == '-----Related Tasks-----':
            break

        fields = []
        line = __CSVLine(line)
        while line.has_next():
            fields.append(line.next())

        if len(fields) < 6:
            continue

        lat = __parse_coordinate(fields[3]);
        if bounds and (lat > bounds.top or lat < bounds.bottom):
            continue

        lon = __parse_coordinate(fields[4]);
        if bounds and (lon > bounds.right or lon < bounds.left):
            continue

        wp = Waypoint()
        wp.lat = lat;
        wp.lon = lon;
        wp.altitude = __parse_altitude(fields[5]);
        wp.name = fields[0].strip();
        wp.country_code = fields[2].strip();
        
        if len(fields) > 7 and len(fields[7]) > 0:
            wp.runway_dir = int(fields[7]);

        if len(fields) > 8 and len(fields[8]) > 0:
          wp.runway_len = __parse_length(fields[8]);
        waypoint_list.append(wp)
        
    return waypoint_list