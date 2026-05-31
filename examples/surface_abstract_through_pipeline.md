# Surface paper abstract through the Come pipeline

A live, end-to-end run of the Hypothesis Surface paper abstract through the OpenCog tokenize → adapter → ONA reasoner → adapter integration in this repository.

This is **performative**, not a substantive empirical result. It demonstrates that the pipeline is real, the integration is end to end, and the perturbation-tested adapter seam is operational against a real cognitive-architecture reasoner running real Narsese inference. It is offered as a good-faith operational answer to AGI-26 Reviewer 3's call for `[1]` (the Cost of Cacophony) and `[41]` (companion proofs) to be made directly verifiable in form.

## Pipeline mode

| Stage | Mode | Substrate |
|---|---|---|
| OpenCog tokenize | mock (whitespace fallback on uncached input) | Python port of `tokenize-text` at https://github.com/PaulTiffany/learn/tree/perturbation-testing-starter |
| Adapter: tokens → Narsese | mutation-tested (16 oracle fixtures, all passing) | `come/adapters.py` `tokens_to_narsese` |
| ONA inference | **live** | OpenNARS-for-Applications binary at `~/ONA/NAR` (WSL2 Ubuntu, built from upstream per `agent_reports/ona_build.md`) |
| Adapter: ONA → result | mutation-tested (same 16 fixtures, including 3 real-format cases) | `come/adapters.py` `inferences_to_result` |

## Input

The full Hypothesis Surface abstract, LaTeX-stripped to plain prose. 1194 characters, roughly 200 words. Source: `examples/surface_abstract.txt`.

## Run

```
COME_NARS_MODE=live COME_NARS_STEPS=20 COME_NARS_TIMEOUT=180 python examples/run_surface.py
```

Reproduction requires WSL2 Ubuntu with the ONA binary built per upstream `build.sh`. See `agent_reports/ona_build.md` in the AGI-26 paper repo for the friction notes (CRLF line endings, missing `-f` flag on `rm`).

## Output stats

| Metric | Value |
|---|---|
| Input characters | 1194 |
| OpenCog tokens (after wall) | 163 |
| Narsese statements emitted | 161 |
| ONA raw output lines | 763 |
| Derived inferences (filtered) | 416 |
| Mean frequency | 1.0000 |
| Mean confidence | 0.7210 |

The Input echoes and Selected internal-scheduling lines from ONA's 763 total are filtered by the adapter; only the 416 Derived lines count as inferences.

## Sample high-confidence derivations

Top 15 by confidence, all at ONA's deduction confidence ceiling of 0.81:

```
0.8100  <"A" --> (follows /1 "resource-bounded")>.
0.8100  <"resource-bounded" --> (follows /2 "A")>.
0.8100  <"resource-bounded" --> (follows /1 "agent")>.
0.8100  <"agent" --> (follows /2 "resource-bounded")>.
0.8100  <"agent" --> (follows /1 "that")>.
0.8100  <"that" --> (follows /2 "agent")>.
0.8100  <"that" --> (follows /1 "differentiates")>.
0.8100  <"differentiates" --> (follows /2 "that")>.
0.8100  <"differentiates" --> (follows /1 "its")>.
0.8100  <"its" --> (follows /2 "differentiates")>.
0.8100  <"its" --> (follows /1 "input")>.
0.8100  <"input" --> (follows /2 "its")>.
0.8100  <"input" --> (follows /1 "into")>.
0.8100  <"into" --> (follows /2 "input")>.
0.8100  <"into" --> (follows /1 "claims")>.
```

These are the projection-style derivations ONA produces from each `<(*, "a", "b") --> follows>.` input statement (extracting both `a` and `b` as participants in the relation). At lower confidences ONA derived 401 further statements including inheritance reversals, similarity statements, products, and multi-step compositions across the abstract's word adjacency graph.

## What this is and is not

**Is.** A working integration of two of the longest-running symbolic-AGI research projects (OpenCog and OpenNARS) glued by mutation-tested Python adapters. The Surface paper's own abstract is the input. The output is a structured trace verifiable against the real ONA binary.

**Is not.** A claim that this analysis tells us anything substantive about the Surface framework. The OpenCog stage uses a whitespace fallback (not the full atomspace-backed parser); the Narsese encoding (`follows` predicate on adjacent words) is the simplest possible adjacency lift, not a meaningful semantic encoding; the ONA reasoner with default config produces structural inferences that follow from this encoding rather than reasoning about the framework's claims.

**Means.** The integration substrate is real. The adapter seam is real. The adequacy gate (perturbation testing) is meaningful at the seam. Future work can replace the OpenCog stage with a full atomspace parse and replace the Narsese encoding with a richer semantic lift; the adapter contract does not need to change. Each replacement is one bridge, one oracle, one mutmut run, one commit.

## Full trace

`examples/surface_abstract_trace.json` contains the complete structured output of every stage: input string, all 163 tokens, all 161 Narsese statements, all 763 raw ONA lines, and all 416 parsed derivations with their truth values.
