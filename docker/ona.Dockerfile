# Stub. See docker/README.md.
# Full image will clone opennars/OpenNARS-for-Applications and build the binary.

FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    build-essential git \
    && rm -rf /var/lib/apt/lists/*

# Stub: real build steps go here when the Live Mode follow-up lands.
CMD ["echo", "ona stub image. See docker/README.md."]
