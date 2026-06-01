# GSM8K reasoning benchmark trace through the Come pipeline

A live cross-run demonstrating that the GSM8K grade-school math reasoning benchmark (Cobbe et al. 2021) and this repository's integration pipeline can be composed end to end. The output of one becomes the input of the other.

This is companion evidence for the AGI-26 paper's Future Work commitment: *"Standing with benchmarks, not against."*

## Pipeline composition

```
GSM8K test split (HuggingFace datasets) -> 5 problems
  -> narrative renderer (one sentence per question, one per answer)
    -> Come pipeline
       -> OpenCog tokenize (mock with whitespace fallback)
       -> tokens_to_narsese adapter (mutation-tested)
       -> NARS (mock: echo as facts at confidence 0.90)
       -> inferences_to_result adapter (mutation-tested)
    -> structured derived inferences
```

## Run

```python
from datasets import load_dataset
ds = load_dataset("gsm8k", "main", split="test")
problems = [ds[i] for i in range(5)]
# render to narrative, then:
from come.pipeline import run as come_run
trace = come_run(narrative)
```

The first five GSM8K test problems are flattened into a single narrative, one sentence per question (first-sentence summary) and one per reference answer (final numeric result):

> "Problem 0 asks Janet's ducks lay 16 eggs per day. The reference solution reaches the final answer 18. Problem 1 asks A robe takes 2 bolts of blue fiber and half that much white fiber. The reference solution reaches the final answer 3. ..."

Then fed to `come.pipeline.run`.

## Output stats

| Metric | Value |
|---|---|
| Input chars (narrative) | 672 |
| GSM8K problems | 5 |
| OpenCog tokens | 118 |
| Narsese statements emitted | 116 |
| NARS raw lines | 116 |
| Derived inferences (filtered) | 116 |
| Mean confidence | 0.9000 |

## What this is and is not

**Is.** A working composition of a standard reasoning benchmark (GSM8K) and this repository's pipeline. Both codes ran. The output of `datasets.load_dataset` became the input of Come. The integration substrate ingests benchmark-format text and produces μ-trackable output.

**Is not.** A measurement of solver accuracy on GSM8K. We are not solving the math problems. We are not calling an LLM. The narrative renderer is a thin text flattening of the problem and reference answer, not a reasoning trace. The NARS stage is in mock mode (echo as facts). The 0.90 confidence is the mock confidence, not a measurement of arithmetic correctness.

**Means.** The "Standing with benchmarks, not against" stance in the AGI-26 Future Work paragraph is operational, not aspirational. The cross-pipeline substrate accepts benchmark-format input today. Deeper integration (a real solver upstream, real ONA downstream, a richer renderer that preserves the chain-of-thought structure) is the natural next step. "More to come" names the integration work as ongoing collaboration, not as opposition.

## Reproduction

1. `pip install datasets`
2. `pip install -r requirements.txt && python examples/run_gsm8k_cross.py`

## Related

- AGI-26 paper Future Work: cites this run via `\cite{tiffany2026come}`.
- GSM8K reference: Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H., Kaiser, L., Plappert, M., Tworek, J., Hilton, J., Nakano, R., Hesse, C., Schulman, J. *Training Verifiers to Solve Math Word Problems.* arXiv:2110.14168, 2021.
- The PyMDP active-inference trace was previously run through this same pipeline; see `pymdp_trace_through_pipeline.md`.
- The Surface paper abstract was also run through this pipeline; see `surface_abstract_through_pipeline.md`.
