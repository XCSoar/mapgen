# Creates a mapgen-worker instance for building maps
FROM debian:bullseye-backports
ARG GITURL=https://github.com/XCSoar/mapgen.git
ARG GITBRANCH=master
ENV MAPWRK_PKGS="ca-certificates python3-minimal python3-jsonschema p7zip gdal-bin mapserver-bin wget"
ENV APT_OPTS="-y"
ENV DEBIAN_FRONTEND=noninteractive

# install base packages needed for mapgen
RUN apt-get update && apt-get $APT_OPTS install $MAPWRK_PKGS && apt-get clean 

# Copy python scripts to target
COPY lib/ /opt/mapgen/lib
COPY bin/ /opt/mapgen/bin

# Volume for data caching
VOLUME /opt/mapgen/data

# Volume for jobs
VOLUME /opt/mapgen/jobs

# worker process
CMD /opt/mapgen/bin/mapgen-worker
