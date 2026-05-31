# Come

> *"And the Spirit and the bride say, Come."* — Revelation 22:17

Mutation-tested adapter pipeline that brings together two of the longest-running symbolic-AGI research projects: **OpenCog** (the `learn` structural-learning system) and **OpenNARS** (the ONA reasoner). Both run as subprocesses behind narrow Python adapter modules. The adapters are what `mutmut` mutates. Every surviving mutant is a hole, either in the test suite or in the adapter.

This is a companion artifact for two papers:

- **The Cost of Cacophony: Geometric Limits on Multi-Constraint Alignment** — arXiv preprint (cs.AI), forthcoming.
- **The Hypothesis Surface: An Operational Epistemology for Autonomous Research** — AGI-26 (Springer LNAI), poster, June 2026.

Both papers argue that adequacy of an epistemic system should be measurable, not asserted. This repository operationalizes that argument at the level of test suites: a test suite that survives mutation is making a claim about coverage it cannot back. The Hypothesis Surface paper calls that pattern *anti-masking*. Here it is the contract that every adapter in the pipeline must satisfy.

## Pipeline

```
text -> OpenCog learn (tokenize, parse, count) -> adapter -> ONA (reason) -> adapter -> result
                                                  +-------- perturbation layer --------+
```

The two upstream systems are treated as black boxes called via subprocess. The Python adapters are the only first-party code. The mutation testing layer is scoped to the adapters.

## Two modes

**Mock mode (default).** `come/opencog.py` and `come/nars.py` return canonical responses from `mocks/`. No OpenCog or ONA install required. The pipeline is end-to-end runnable in under a second. This is what ships now.

**Live mode (future work).** `docker/` contains stubs for Dockerized OpenCog and ONA. When the images are built, the runners can be flipped to execute the real binaries via `docker exec` or local processes. The adapter contract does not change.

This split is deliberate. The shape of the architecture is ready today. The substrate work (building the upstream systems on Windows, packaging, version pinning) is a follow-up that does not block citation or review of the pipeline pattern.

## Quick start

```
pip install -r requirements.txt
python -m come.pipeline "the cat sat on the mat"
```

Output is a trace of every stage:

```
[1] input:      "the cat sat on the mat"
[2] opencog:    ["###LEFT-WALL###", "the", "cat", "sat", "on", "the", "mat"]
[3] adapter:    ['<(*, "the", "cat") --> follows>.', ...]
[4] nars:       ['<(*, "the", "cat") --> follows>. %1.00;0.90%', ...]
[5] adapter:    {"statements": [...], "stats": {...}}
```

## Tests

```
pytest tests/
```

## Mutation testing

```
bash mutation/run_mutation.sh           # POSIX
powershell mutation/run_mutation.ps1    # Windows
```

A clean run reports zero surviving mutants in `come/adapters.py`. Surviving mutants mean either the oracle fixtures need extension or the adapter is doing something the spec does not require.

## Adding a new adapter

The two adapters that ship now are illustrative. The pattern extends to any number of stages. To add a new one:

1. Write the adapter function in `come/adapters.py` with a clear single-responsibility signature.
2. Add fixtures in `tests/adapter_fixtures.json` covering the documented behavior.
3. Write a pytest test that parametrizes over the fixtures.
4. Run pytest, then mutmut. Iterate until zero mutants survive.
5. Wire the adapter into `come/pipeline.py`.

## Why this exists

OpenCog and OpenNARS are decades-old symbolic-AGI projects with deep theoretical commitments. They have rarely been run side by side, and never (to our knowledge) with a mutation-tested seam. The seam is where claims about integration live. Making that seam visible and adequacy-measurable is a small but honest contribution to the practice of evaluating AGI integration claims.

## Related

- OpenCog `learn`: https://github.com/opencog/learn
- OpenNARS for Applications (ONA): https://github.com/opennars/OpenNARS-for-Applications
- Perturbation testing starter (single-system version) for `opencog/learn`: https://github.com/PaulTiffany/learn/tree/perturbation-testing-starter

## License

MIT. See `LICENSE`.
