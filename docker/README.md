# Docker integration (future work)

This directory contains stubs for Dockerized OpenCog and OpenNARS. When the images are built and tested, the runners in `come/opencog.py` and `come/nars.py` can be flipped from mock mode to live mode without changing their signatures.

## Status

Both Dockerfiles are skeletons. Building either takes a non-trivial dependency walk:

- **OpenCog learn** needs `cogutil`, `atomspace`, `ure`, and Guile. The upstream `opencog/learn` README and CMakeLists are the source of truth.
- **OpenNARS for Applications (ONA)** is a C codebase with a Makefile build. The compiled binary takes Narsese on stdin and emits inferences on stdout, which is the contract our mock simulates.

## Plan when live mode is wired

1. Build images: `docker build -t come/opencog -f opencog.Dockerfile .` and similarly for ONA.
2. Add a `LIVE_MODE=1` environment variable that the runners check.
3. In live mode, the runner constructs a `docker exec` command (or uses `docker.from_env()` via the Python SDK) and pipes stdin / collects stdout.
4. The adapter contract does not change. The mocks become regression fixtures.

The mock-first design is deliberate. Mutation testing of the adapter layer does not need live upstream systems to be meaningful. Live mode is a follow-up that strengthens but does not gate the core contribution.
