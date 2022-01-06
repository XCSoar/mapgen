# Creates a mapgen-worker instance for building maps
FROM debian:bullseye-slim
ENV MAPWRK_PKGS="ca-certificates python3-jsonschema python3-requests p7zip gdal-bin mapserver-bin wget"
ENV DEBIAN_FRONTEND=noninteractive

# install base packages needed for mapgen
RUN apt-get update && apt install -y --no-install-recommends $MAPWRK_PKGS && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy python scripts of mapgen to target
COPY lib/ /opt/mapgen/lib/
COPY bin/ /opt/mapgen/bin/

# Volume for data caching and jobs
VOLUME /opt/mapgen/data
VOLUME /opt/mapgen/jobs

# worker process
ENTRYPOINT ["/opt/mapgen/bin/mapgen-worker"]
