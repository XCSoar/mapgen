# Creates a mapgen-worker instance for building maps
FROM debian:bullseye-backports
ARG GITURL=https://github.com/XCSoar/mapgen.git
ARG GITBRANCH=master
ENV APT_OPTS="-y"
ENV MAPFRNT_PKG="ca-certificates python3-minimal python3-cherrypy3 python3-genshi"
ENV DEBIAN_FRONTEND=noninteractive

# Deploy Mapgen
RUN apt-get update && apt install -y $MAPFRNT_PKG && apt-get clean 

# use git during install only smaller size
COPY lib/ /opt/mapgen/lib/
COPY bin/ /opt/mapgen/bin/

## Volume for jobs used by mapgen-worker
VOLUME /opt/mapgen/jobs

# Nginx for reverse proxy
RUN apt-get $APT_OPTS install nginx && apt-get clean
COPY ./container/frontend/files/default /etc/nginx/sites-available/default 
RUN ln -fs /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

EXPOSE 9090

# Supervisord for running two processes inside container
RUN apt-get $APT_OPTS install supervisor && apt-get clean
RUN mkdir -p /var/log/supervisor
COPY ./container/frontend/files/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Launch supervisord on container startup
CMD ["/usr/bin/supervisord"]
