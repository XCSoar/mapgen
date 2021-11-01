# Creates a mapgen-worker instance for building maps
FROM debian:stretch-backports
ARG GITURL=https://github.com/XCSoar/mapgen.git
ARG GITBRANCH=master
ENV MAPWRK_PKGS="ca-certificates python-minimal python-jsonschema p7zip gdal-bin mapserver-bin wget"
ENV APT_OPTS="-y"
ENV DEBIAN_FRONTEND=noninteractive

# install base packages needed for mapgen
RUN apt-get update && apt-get $APT_OPTS install $MAPWRK_PKGS && apt-get clean 

# use git during install only smaller size
RUN apt install -y git && git clone $GITURL -b $GITBRANCH /opt/mapgen/ && apt-get -y purge git && apt-get -y autoremove && apt-get clean

# Volume for data caching
VOLUME /opt/mapgen/data

# Volume for jobs
VOLUME /opt/mapgen/jobs

# worker process
CMD /opt/mapgen/bin/mapgen-worker
