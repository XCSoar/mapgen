
# Map generator for XCSoar

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/099ae14d05e6426d82080c5e1074e38c)](https://app.codacy.com/gh/XCSoar/mapgen?utm_source=github.com&utm_medium=referral&utm_content=XCSoar/mapgen&utm_campaign=Badge_Grade_Settings)

This generates maps in the xcm format for [XCSoar](https://xcsoar.org/) a tactical
Gliding computer.

The Maps are layered out of a multitude of sources:

* terrain SRTM
* topology VMAP0
* Roads and Towns OSM
* Waypoints CUP format
* Airspaces OPENAIR format

## Deployment and Development

## Ansible

To aid development and deployment an accompaning repositorty was created:
[XCSoar Mapgen Ansible](https://github.com/xcsoar/xcsoar-mapgen-ansible)

The ansible-role can be played back onto a Debian system in order to deploy
mapgen. An alternative is the vagrantfile in that repository which allows you
to download and install a vm, including provisioning of mapgen.
![Docker](https://github.com/XCSoar/xcsoar-mapgen-container/workflows/Docker/badge.svg)

## Container

### Frontend

The frontend container contains the cherrypy based service and an nginx based
reverse proxy for exposing the mapgen on port 9090 Both processes in the
frontend container are started by supervisord.

Frontend produces job files that are put into a shared volume

```
/opt/mapgen/jobs/<jobid>.queued
```

### Worker

This is the actual map builder, that takes the queued jobs in
/opt/mapgen/jobs/jobid and starts processing all the *.queued jobs.

### Volumes

These are named volumes inside your docker service.

```
/opt/mapgen/jobs:
```

 This is the job directory where all jobs get stored

```
/opt/mapgen/data:
```

 This directory caches all the data from the data repository. WARNING: This
 volume can take up a lot of space (100GB).

### Ports

```
Port 9090
```

### Build Variables

The Following build variables can be set during build (optional):

1. GITURL - The git url for the mapgen sources
   Default: [Mapgen git](https://github.com/xcsoar/mapgen/mapgen.git)
1. GITBRANCH - The branch name
   Default: master

#### Building

in the current directory:

```bash
docker-compose build
```

or with options:

```bash
docker-compose build \
--build-arg=GITURL=https://github.com/myuser/mapgen/mapgen.git \
--build-arg=GITBRANCH=myfeature
```

#### Starting

```bash
docker-compose up -d
```
