
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/099ae14d05e6426d82080c5e1074e38c)](https://app.codacy.com/gh/XCSoar/mapgen?utm_source=github.com&utm_medium=referral&utm_content=XCSoar/mapgen&utm_campaign=Badge_Grade_Settings)
# mapgen [![Codacy Badge](https://app.codacy.com/project/badge/Grade/61ac47282af44f0f9897d80b0d229e2d)](https://www.codacy.com/gh/XCSoar/mapgen/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=XCSoar/mapgen&amp;utm_campaign=Badge_Grade)
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
