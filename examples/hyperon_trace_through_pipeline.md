# OpenCog Hyperon (MeTTa) trace through the Come pipeline

A live cross-run demonstrating that Ben Goertzel's modern OpenCog rewrite (Hyperon, MeTTa runtime) and this repository's integration pipeline can be composed end to end. The output of one becomes the input of the other.

This is companion evidence for the AGI-26 paper's Future Work commitment: *"Standing with benchmarks, not against."* Hyperon is the AGI flagship project in the H+ / cosmist orbit, and AGI-26 is the conference Goertzel runs. This run threads that lineage through our pipeline as operational composition.

## Pipeline composition

```
Hyperon MeTTa runtime (hyperon 0.2.10, Python 3.11 wheel)
  -> 5-query atomspace sequence (arithmetic, match, rule, conditional, equality)
    -> narrative renderer (text)
      -> Come pipeline
         -> OpenCog tokenize (mock with whitespace fallback)
         -> tokens_to_narsese adapter (mutation-tested)
         -> NARS (mock: echo as facts at confidence 0.90)
         -> inferences_to_result adapter (mutation-tested)
      -> structured derived inferences
```

## Run

```python
from hyperon import MeTTa
m = MeTTa()
m.run('!(+ 2 3)')                                       # arithmetic
m.run('(Parent Tom Bob)')
m.run('(Parent Bob Alice)')
m.run('!(match &self (Parent Tom $x) $x)')              # atomspace match
m.run('(= (grandparent $a $c) (, (Parent $a $b) (Parent $b $c)))')
m.run('!(grandparent Tom Alice)')                       # rule application
m.run('!(if (> 5 3) yes no)')                           # conditional
m.run('!(== (+ 1 1) 2)')                                # equality
```

The MeTTa trace is rendered as one sentence per query and one sentence per result:

> "At query 0 the MeTTa runtime received arithmetic input !(+ 2 3). The atomspace returned result [[5]] for that query. At query 1 the MeTTa runtime received atomspace_match input ..."

Then fed to `come.pipeline.run`.

## Output stats

| Metric | Value |
|---|---|
| Input chars (narrative) | 703 |
| MeTTa queries | 5 |
| OpenCog tokens | 115 |
| Narsese statements emitted | 108 |
| NARS raw lines | 108 |
| Derived inferences (filtered) | 108 |
| Mean confidence | 0.9000 |

## What this is and is not

**Is.** A working composition of the Hyperon MeTTa atomspace reasoner and this repository's pipeline. Both codes ran. The output of Hyperon became the input of Come. The integration substrate is real. This demonstrates that the H+ cognitive architecture lineage (OpenCog, Hyperon, MeTTa, AGI-26) can be threaded through our pipeline as operational composition.

**Is not.** A claim that Hyperon's MeTTa reasoner and our pipeline have semantic equivalence. The narrative renderer is a thin text flattening of MeTTa query strings and result strings, not a translation of MeTTa atomspace semantics into Narsese. The NARS stage is in mock mode (echo as facts). The 0.90 confidence is the mock confidence, not a measurement of MeTTa reasoning correctness or atomspace truth values.

**Means.** The "Standing with benchmarks, not against" stance in the AGI-26 Future Work paragraph is operational, not aspirational. The cross-pipeline substrate is here today and runs against the actual Hyperon runtime, not a stub. Deeper semantic integration (real ONA plus a renderer that preserves MeTTa typing and atomspace links) is the natural next step. "More to come" names the integration work as ongoing collaboration with the H+ / cosmist AGI program, not as opposition.

## Reproduction

1. `py -3.11 -m pip install hyperon` (3.13 wheel not yet on PyPI for Windows as of 2026-06)
2. `pip install -r requirements.txt`
3. `py -3.11 examples/run_hyperon_cross.py`

## Related

- AGI-26 paper Future Work: cites this run via `\cite{tiffany2026come}`.
- Hyperon reference: Goertzel, B., Bogdanov, V., Duncan, M., et al. *OpenCog Hyperon: A Framework for AGI at the Human Level and Beyond.* arXiv:2310.18318 (2023).
- The PyMDP active-inference trace was previously run through this same pipeline; see `pymdp_trace_through_pipeline.md`.
- The Surface paper abstract was previously run through this same pipeline; see `surface_abstract_through_pipeline.md`.
