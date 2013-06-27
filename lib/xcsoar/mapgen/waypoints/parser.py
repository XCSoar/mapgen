from xcsoar.mapgen.waypoints.seeyou_reader import parse_seeyou_waypoints
from xcsoar.mapgen.waypoints.winpilot_reader import parse_winpilot_waypoints


def parse_waypoint_file(filename, file=None):
    if not file:
        file = open(filename, 'r')

    if filename.lower().endswith('.xcw') or filename.lower().endswith('.dat'):
        return parse_winpilot_waypoints(file)
    elif filename.lower().endswith('.cup'):
        return parse_seeyou_waypoints(file)
    else:
        raise RuntimeError('Waypoint file {} has an unsupported format.'.format(filename))
