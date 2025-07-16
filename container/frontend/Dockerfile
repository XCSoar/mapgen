# Creates a mapgen-worker instance for building maps
FROM debian:bookworm-slim
ENV MAPFRNT_PKG="ca-certificates python3-cherrypy3 python3-genshi"
ENV DEBIAN_FRONTEND=noninteractive

# Deploy Mapgen
RUN apt-get update && apt-get install -y --no-install-recommends $MAPFRNT_PKG && apt-get clean && rm -rf /var/lib/apt/lists/*

# use git during install only smaller size
COPY lib/ /opt/mapgen/lib/
COPY bin/ /opt/mapgen/bin/

## Volume for jobs used by mapgen-worker
VOLUME /opt/mapgen/jobs

EXPOSE 9090

# Launch supervisord on container startup
CMD ["/opt/mapgen/bin/mapgen-server"]
