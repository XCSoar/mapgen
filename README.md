# mapgen
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
