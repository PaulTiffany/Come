"""
Run the Hypothesis Surface paper abstract through the Come pipeline.

This script reads `surface_abstract.txt`, feeds it through the OpenCog mock
tokenizer, the perturbation-tested tokens_to_narsese adapter, the live ONA
reasoner (via WSL by default), and the perturbation-tested
inferences_to_result adapter. It writes a structured JSON trace next to itself.

Usage:
    COME_NARS_MODE=live python examples/run_surface.py
or mock-only:
    python examples/run_surface.py

The output goes to `examples/surface_abstract_trace.json` and a human-readable
summary is written to stdout.
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from come.pipeline import run  # noqa: E402


HERE = pathlib.Path(__file__).resolve().parent


def main():
    abstract = (HERE / "surface_abstract.txt").read_text(encoding="utf-8").strip()
    trace = run(abstract)

    out_path = HERE / "surface_abstract_trace.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2)

    stats = trace["result"]["stats"]
    n_tokens = len(trace["opencog_tokens"])
    n_narsese = len(trace["narsese_in"])
    n_nars_out = len(trace["nars_inferences"])

    print(f"input chars:        {len(trace['input'])}")
    print(f"opencog tokens:     {n_tokens}")
    print(f"narsese statements: {n_narsese}")
    print(f"nars raw lines:     {n_nars_out}")
    print(f"derived inferences: {stats['count']}")
    print(f"mean frequency:     {stats['mean_freq']:.4f}")
    print(f"mean confidence:    {stats['mean_conf']:.4f}")
    print(f"trace written to:   {out_path}")


if __name__ == "__main__":
    main()
