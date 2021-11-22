# Creates a mapgen-worker instance for building maps
FROM debian:bullseye-slim
ENV MAPFRNT_PKG="ca-certificates python3-cherrypy3 python3-genshi"
ENV NGINX_PKG="nginx"
ENV SUPERVISOR_PKG="supervisor"
ENV DEBIAN_FRONTEND=noninteractive

# Deploy Mapgen
RUN apt-get update && apt-get install -y --no-install-recommends $MAPFRNT_PKG $NGINX_PKG $SUPERVISOR_PKG && apt-get clean && rm -rf /var/lib/apt/lists/*

# use git during install only smaller size
COPY lib/ /opt/mapgen/lib/
COPY bin/ /opt/mapgen/bin/

## Volume for jobs used by mapgen-worker
VOLUME /opt/mapgen/jobs

# Nginx for reverse proxy
COPY ./container/frontend/files/default /etc/nginx/sites-available/default 
RUN ln -fs /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

EXPOSE 9090

# Supervisord for running two processes inside container
RUN mkdir -p /var/log/supervisor
COPY ./container/frontend/files/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Launch supervisord on container startup
CMD ["/usr/bin/supervisord"]
