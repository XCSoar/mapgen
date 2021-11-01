# Creates a mapgen-worker instance for building maps
FROM debian:stretch-backports
ARG GITURL=https://github.com/XCSoar/mapgen.git
ARG GITBRANCH=master
ENV APT_OPTS="-y"
ENV MAPFRNT_PKG="ca-certificates python-minimal python-cherrypy3 python-genshi"
ENV DEBIAN_FRONTEND=noninteractive

# Deploy Mapgen
RUN apt-get update && apt install -y $MAPFRNT_PKG && apt-get clean 

# use git during install only smaller size
RUN apt-get install -y git && git clone $GITURL -b $GITBRANCH /opt/mapgen/ && apt-get -y purge git && apt-get -y autoremove && apt-get clean

## Volume for jobs used by mapgen-worker
VOLUME /opt/mapgen/jobs

# Nginx for reverse proxy
RUN apt-get $APT_OPTS install nginx && apt-get clean
COPY files/default /etc/nginx/sites-available/default 
RUN ln -fs /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

EXPOSE 9090

# Supervisord for running two processes inside container
RUN apt-get $APT_OPTS install supervisor && apt-get clean
RUN mkdir -p /var/log/supervisor
COPY files/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Launch supervisord on container startup
CMD ["/usr/bin/supervisord"]
