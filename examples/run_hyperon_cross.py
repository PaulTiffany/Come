"""
Cross-run: OpenCog Hyperon (MeTTa) reasoner trace through the Come pipeline.

Standing with benchmarks, not against. The output of one repository's code
becomes the input of the other's. Reproducible with `pip install hyperon`
(Python 3.11 wheel; not yet built for 3.13 on Windows as of 2026-06).

Hyperon is Ben Goertzel's modern OpenCog rewrite, the AGI flagship in the
H+ / cosmist orbit. AGI-26 is the conference Goertzel runs. MeTTa is the
meta-type-theoretic language at its core.
"""

import json
import pathlib
import sys

from hyperon import MeTTa

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from come.pipeline import run as come_run  # noqa: E402


HERE = pathlib.Path(__file__).resolve().parent


def metta_trace():
    """Run a 5-query MeTTa sequence: arithmetic, atomspace match, rule, conditional, equality."""
    m = MeTTa()
    trace = []

    q1 = "!(+ 2 3)"
    r1 = m.run(q1)
    trace.append({"query": q1, "result": str(r1), "kind": "arithmetic"})

    m.run("(Parent Tom Bob)")
    m.run("(Parent Bob Alice)")
    q2 = "!(match &self (Parent Tom $x) $x)"
    r2 = m.run(q2)
    trace.append({"query": q2, "result": str(r2), "kind": "atomspace_match"})

    m.run("(= (grandparent $a $c) (, (Parent $a $b) (Parent $b $c)))")
    q3 = "!(grandparent Tom Alice)"
    r3 = m.run(q3)
    trace.append({"query": q3, "result": str(r3), "kind": "rule_application"})

    q4 = "!(if (> 5 3) yes no)"
    r4 = m.run(q4)
    trace.append({"query": q4, "result": str(r4), "kind": "conditional"})

    q5 = "!(== (+ 1 1) 2)"
    r5 = m.run(q5)
    trace.append({"query": q5, "result": str(r5), "kind": "equality"})

    return trace


def render_narrative(trace):
    """Flatten the MeTTa trace into one English sentence per query plus one per result."""
    parts = []
    for i, entry in enumerate(trace):
        parts.append(
            f"At query {i} the MeTTa runtime received {entry['kind']} input {entry['query']}."
        )
        parts.append(
            f"The atomspace returned result {entry['result']} for that query."
        )
    return " ".join(parts)


def main():
    trace = metta_trace()
    narrative = render_narrative(trace)
    come_trace = come_run(narrative)

    artifact = {
        "hyperon_version": "0.2.10",
        "python": "3.11",
        "metta_trace": trace,
        "narrative": narrative,
        "come_result": come_trace["result"],
        "stats": {
            "metta_queries": len(trace),
            "narrative_chars": len(narrative),
            "opencog_tokens": len(come_trace["opencog_tokens"]),
            "narsese_statements": len(come_trace["narsese_in"]),
            "nars_raw_lines": len(come_trace["nars_inferences"]),
            "derived_inferences": come_trace["result"]["stats"]["count"],
            "mean_confidence": come_trace["result"]["stats"]["mean_conf"],
        },
    }

    out = HERE / "hyperon_cross_trace.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    stats = artifact["stats"]
    print(f"metta queries:      {stats['metta_queries']}")
    print(f"narrative chars:    {stats['narrative_chars']}")
    print(f"opencog tokens:     {stats['opencog_tokens']}")
    print(f"narsese statements: {stats['narsese_statements']}")
    print(f"derived inferences: {stats['derived_inferences']}")
    print(f"mean confidence:    {stats['mean_confidence']:.4f}")
    print(f"trace written to:   {out}")


if __name__ == "__main__":
    main()
