# Come

*All of us is limited. None of us has all the answers. Come develop with us.*

> *And the Spirit and the bride say, Come.* — Revelation 22:17 (KJV)

Mutation-tested adapter pipeline that brings together two of the longest-running symbolic-AGI research projects: **OpenCog** (the `learn` structural-learning system) and **OpenNARS** (the ONA reasoner). Both run as subprocesses behind narrow Python adapter modules. The adapters are what `mutmut` mutates. Every surviving mutant is a hole, either in the test suite or in the adapter.

This is a companion artifact for two papers:

- **The Cost of Cacophony: Geometric Limits on Multi-Constraint Alignment** — arXiv preprint (cs.AI), forthcoming.
- **The Hypothesis Surface: An Operational Epistemology for Autonomous Research** — AGI-26 (Springer LNAI), poster, June 2026.

Both papers argue that adequacy of an epistemic system should be measurable, not asserted. This repository operationalizes that argument at the level of test suites: a test suite that survives mutation is making a claim about coverage it cannot back. The Hypothesis Surface paper calls that pattern *anti-masking*. Here it is the contract that every adapter in the pipeline must satisfy.

## Why this pattern is load-bearing

Constituting a "perfect paper" is a paradox drive if authors and readers are disjoint.

The academic convention asks authors to deliver an artifact immune to criticism, but the author has no privileged access to what a future reader will find broken. That disjointness makes the demand for perfection a paradox driver: a tension unresolvable from inside, only by reframing.

The reframing this repository operationalizes is integration. Authors and readers stop being disjoint when they share a substrate the reader can mutate and verify. Every adapter ships with its test suite. Every surviving mutant is an invitation to find a hole the author did not. Anti-masking is the contract that keeps the integration honest: the author may not assert what the test suite cannot back, and the reader may not dismiss what they have not run.

This repository is incomplete by construction. The work of integrating author and reader is by definition not finished. The invitation in the epigraph is the form of that incompleteness.

## Eight billion manifestos

In *The Consciousness Explosion: A Mindful Human's Guide to the Coming Technological and Experiential Singularity* (Goertzel and Montes, Humanity+, 2024, p. 11), the authors title a section **"Let 8 billion manifestos bloom"** and write:

> we should not be closely adhering to anybody's manifesto. We should each be doing our best to understand and figure things out on our own — based on valuable input from everyone around us.

Tiffany's response on receiving the book:

> Let 8 billion manifestos bloom. Growing beautiful whilst rooted, so that we may cross-pollinate and thrive for a time.

This repository is one such manifesto in operational form. Rooted in the cosmist tradition Goertzel names a page later (Ten Cosmist Convictions, p. 12, with Prisco), it blooms outward as a runnable substrate, offered for cross-pollination with whoever extends it. Each adapter is a bloom: mutable, verifiable, finite. The author-reader integration named in the paradox-drive section above is the manifesto-bloom integration at code altitude. Cross-pollination is the pipeline. Thriving for a time is the honest scope.

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

The code, configurations, mocks, fixtures, and documentation in this repository are released under the **MIT License** (see `LICENSE`).

Paper content and supplementary materials from the AGI-26 and Cost of Cacophony submissions, including the Hypothesis Surface companion materials at https://paultiffany.github.io/hypothesis-surface-agi26/, are released separately under **Creative Commons Attribution 4.0 International (CC BY 4.0)**. Where material from those papers appears in this repository — notably the abstract excerpt in `examples/surface_abstract.txt` and quotations of paper prose in commentary — it is reproduced under the original CC BY 4.0 terms with attribution to the source.

The two licenses do not conflict. Software gets MIT, scholarly content gets CC BY. This documents the convention rather than changing it.
