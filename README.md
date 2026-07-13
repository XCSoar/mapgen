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

### Frontend

The frontend container contains the cherrypy based service and an nginx based
reverse proxy for exposing the mapgen on port 9090 Both processes in the
frontend container are started by supervisord.

Frontend produces job files that are put into a shared volume

```bash
/opt/mapgen/jobs/<jobid>.queued
```

### Worker

This is the actual map builder, that takes the queued jobs in
/opt/mapgen/jobs/jobid and starts processing all the *.queued jobs.

### Volumes

These are named volumes inside your docker service.

```bash
/opt/mapgen/jobs:
```

 This is the job directory where all jobs get stored

```bash
/opt/mapgen/data:
```

 This directory caches all the data from the data repository. WARNING: This
 volume can take up a lot of space (100GB).

Note: To mount those volumes into a local directory to keep them if the containers are dropped, update the docker compose (change the path as needed):

```bash
volumes:
  mapgen-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /home/user/xcsoar_mapgen/mapgen-data
  mapgen-jobs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /home/user/xcsoar_mapgen/mapgen-jobs
```

### Ports

```bash
Port 9090
```

### Build Variables

The Following build variables can be set during build (optional):

1. GITURL: The git url for the mapgen sources
2. GITBRANCH: The branch name

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

### Mounting the source files into the containers

To speed up the development process, it's possible to mount the folders with the Python sources into the container, which allow automatic reload by CherryPy.
Update the docker-compose:

```bash
...
services:
  mapgen-frontend:
...
    volumes:
      - mapgen-jobs:/opt/mapgen/jobs
      - ./lib:/opt/mapgen/lib
      - ./bin:/opt/mapgen/bin
  mapgen-worker:
    ...
    volumes:
      - mapgen-jobs:/opt/mapgen/jobs
      - mapgen-data:/opt/mapgen/data
      - ./lib:/opt/mapgen/lib
      - ./bin:/opt/mapgen/bin
```
