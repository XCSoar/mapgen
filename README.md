# mapgen

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/2637c9ca421c46e7ad7ca67b07ba1f4a)](https://app.codacy.com/gh/XCSoar/mapgen?utm_source=github.com&utm_medium=referral&utm_content=XCSoar/mapgen&utm_campaign=Badge_Grade_Settings)

Map generator for XCSoar

This generates maps in the xcm format for [https://xcsoar.org/] a tactical Gliding computer.

The Maps are layered out of a multitude of sources:
* terrain SRTM
* topology VMAP0
* Roads and Towns OSM
* Waypoints CUP format
* Airspaces OPENAIR format

## Deployment and Development
To aid development and deployment an accompaning repositorty was created:
[https://github.com/xcsoar/xcsoar-mapgen-ansible]

The ansible-role can be played back onto a Debian system in order to deploy mapgen. An alternative is the
vagrantfile in that repository which allows you to download and install a vm, including provisioning of mapgen. 
