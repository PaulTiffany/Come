"""
Cross-run: PyMDP (Friston/Heins) active-inference trace through the Come pipeline.

Standing with benchmarks, not against. The output of one repository's code
becomes the input of the other's. Reproducible with `pip install
inferactively-pymdp==0.0.7.1`.
"""

import json
import pathlib
import sys

import numpy as np
from pymdp import utils
from pymdp.agent import Agent

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from come.pipeline import run as come_run  # noqa: E402


HERE = pathlib.Path(__file__).resolve().parent


def pymdp_trajectory(steps=5, seed=42):
    """Run a short T-maze trajectory and return a list of per-step records."""
    np.random.seed(seed)
    num_states = [3]
    num_obs = [3]
    num_controls = [3]

    A = utils.random_A_matrix(num_obs, num_states)
    B = utils.random_B_matrix(num_states, num_controls)
    C = utils.obj_array_zeros(num_obs)
    C[0][2] = 4.0
    D = utils.obj_array_uniform(num_states)

    agent = Agent(A=A, B=B, C=C, D=D)
    trace = []
    obs = [0]
    for t in range(steps):
        qs = agent.infer_states(obs)
        q_pi, efe = agent.infer_policies()
        action = agent.sample_action()
        qs_vec = np.array(qs[0]).round(3).tolist()
        q_pi_vec = np.array(q_pi)
        entropy = float(-np.sum(q_pi_vec * np.log(q_pi_vec + 1e-12)))
        trace.append({
            "t": t,
            "obs": int(obs[0]),
            "posterior_states": qs_vec,
            "policy_entropy": entropy,
            "neg_efe": np.array(efe).round(3).tolist(),
            "action": int(np.array(action).flatten()[0]),
        })
        next_state = int(np.argmax(np.array(qs[0])))
        next_obs_dist = np.array(A[0])[:, next_state]
        obs = [int(np.random.choice(num_obs[0], p=next_obs_dist / next_obs_dist.sum()))]
    return trace


def render_narrative(trace):
    """Flatten the PyMDP trace into one English sentence per timestep."""
    parts = []
    for entry in trace:
        parts.append(
            f"At step {entry['t']} the agent observed signal {entry['obs']} "
            f"and inferred posterior over states. It selected action "
            f"{entry['action']} under policy entropy {entry['policy_entropy']:.3f}."
        )
    return " ".join(parts)


def main():
    trace = pymdp_trajectory()
    narrative = render_narrative(trace)
    come_trace = come_run(narrative)

    artifact = {
        "pymdp_trace": trace,
        "narrative": narrative,
        "come_result": come_trace["result"],
        "stats": {
            "pymdp_steps": len(trace),
            "narrative_chars": len(narrative),
            "opencog_tokens": len(come_trace["opencog_tokens"]),
            "narsese_statements": len(come_trace["narsese_in"]),
            "nars_raw_lines": len(come_trace["nars_inferences"]),
            "derived_inferences": come_trace["result"]["stats"]["count"],
            "mean_confidence": come_trace["result"]["stats"]["mean_conf"],
        },
    }

    out = HERE / "pymdp_cross_trace.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    stats = artifact["stats"]
    print(f"pymdp steps:        {stats['pymdp_steps']}")
    print(f"narrative chars:    {stats['narrative_chars']}")
    print(f"opencog tokens:     {stats['opencog_tokens']}")
    print(f"narsese statements: {stats['narsese_statements']}")
    print(f"derived inferences: {stats['derived_inferences']}")
    print(f"mean confidence:    {stats['mean_confidence']:.4f}")
    print(f"trace written to:   {out}")


if __name__ == "__main__":
    main()
