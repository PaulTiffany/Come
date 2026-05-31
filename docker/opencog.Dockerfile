# Stub. See docker/README.md.
# Full image will build cogutil, atomspace, ure, and opencog/learn from upstream.

FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    build-essential cmake git \
    guile-3.0 guile-3.0-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Stub: real build steps go here when the Live Mode follow-up lands.
CMD ["echo", "opencog stub image. See docker/README.md."]
