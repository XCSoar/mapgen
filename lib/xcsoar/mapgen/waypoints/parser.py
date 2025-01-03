# -*- coding: utf-8 -*-
from xcsoar.mapgen.waypoints.seeyou_reader import parse_seeyou_waypoints
from xcsoar.mapgen.waypoints.winpilot_reader import parse_winpilot_waypoints


def parse_waypoint_file(filename, file=None):
    lines = file.readlines()

    if filename.lower().endswith(".xcw") or filename.lower().endswith(".dat"):
        return parse_winpilot_waypoints(lines)
    elif filename.lower().endswith(".cup"):
        return parse_seeyou_waypoints(lines)  # 241207 gfp bugfix:
    else:
        raise RuntimeError(
            "Waypoint file {} has an unsupported format.".format(filename)
        )
