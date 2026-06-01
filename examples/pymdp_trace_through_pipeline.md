# PyMDP active-inference trace through the Come pipeline

A live cross-run demonstrating that Friston/Heins active-inference code (PyMDP) and this repository's integration pipeline can be composed end to end. The output of one becomes the input of the other.

This is companion evidence for the AGI-26 paper's Future Work commitment: *"Standing with benchmarks, not against."*

## Pipeline composition

```
PyMDP (Friston/Heins JAX-free 0.0.7) -> 5-step T-maze trajectory
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
import numpy as np
from pymdp import utils
from pymdp.agent import Agent

np.random.seed(42)
num_states = [3]; num_obs = [3]; num_controls = [3]
A = utils.random_A_matrix(num_obs, num_states)
B = utils.random_B_matrix(num_states, num_controls)
C = utils.obj_array_zeros(num_obs); C[0][2] = 4.0
D = utils.obj_array_uniform(num_states)
agent = Agent(A=A, B=B, C=C, D=D)
# ... 5-step trajectory ...
```

The PyMDP trace is rendered as a sentence per timestep:

> "At step 0 the agent observed signal 0 and inferred posterior over states. It selected action 1 under policy entropy 0.233. At step 1 the agent observed signal 0 ..."

Then fed to `come.pipeline.run`.

## Output stats

| Metric | Value |
|---|---|
| Input chars (narrative) | 614 |
| PyMDP trace steps | 5 |
| OpenCog tokens | 106 |
| Narsese statements emitted | 104 |
| NARS raw lines | 104 |
| Derived inferences (filtered) | 104 |
| Mean confidence | 0.9000 |

## What this is and is not

**Is.** A working composition of Friston/Heins active-inference code and this repository's pipeline. Both codes ran. The output of PyMDP became the input of Come. The integration substrate is real.

**Is not.** A meaningful validation of either system. The narrative renderer is a thin text-flattening of the PyMDP trace, not a semantic translation. The NARS stage is in mock mode (echo as facts). The 0.90 confidence is the mock confidence, not a measurement of active-inference correctness.

**Means.** The "Standing with benchmarks, not against" stance in the AGI-26 Future Work paragraph is operational, not aspirational. The cross-pipeline substrate is here today; deeper semantic integration (real ONA + a richer renderer that preserves the inference structure) is the natural next step. "More to come" names the integration work as ongoing collaboration, not as opposition.

## Reproduction

1. `pip install inferactively-pymdp==0.0.7.1`
2. Run the snippet above (full version in `examples/run_pymdp_cross.py`)
3. `pip install -r requirements.txt && python examples/run_pymdp_cross.py`

## Related

- AGI-26 paper Future Work: cites this run via `\cite{tiffany2026come}`.
- Active inference reference: Heins, C., et al. *pymdp: A Python library for active inference in discrete state spaces.* Journal of Open Source Software 7(73), 4098 (2022).
- The Surface paper abstract was previously run through this same pipeline; see `surface_abstract_through_pipeline.md`.
