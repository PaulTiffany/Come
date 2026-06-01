"""
Cross-run: GSM8K (Cobbe et al. 2021) grade-school math reasoning benchmark
trace through the Come pipeline.

Standing with benchmarks, not against. The output of one repository's code
becomes the input of the other's. Reproducible with `pip install datasets`.

GSM8K citation:
  Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H., Kaiser, L.,
  Plappert, M., Tworek, J., Hilton, J., Nakano, R., Hesse, C., Schulman, J.
  "Training Verifiers to Solve Math Word Problems."
  arXiv:2110.14168, 2021.
"""

import json
import pathlib
import re
import sys

from datasets import load_dataset

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from come.pipeline import run as come_run  # noqa: E402


HERE = pathlib.Path(__file__).resolve().parent


def pull_problems(n=5, seed=0):
    """Pull n problems from the GSM8K test split (deterministic order)."""
    ds = load_dataset("gsm8k", "main", split="test")
    problems = []
    for i in range(n):
        ex = ds[i]
        problems.append({
            "idx": i,
            "question": ex["question"].strip(),
            "answer": ex["answer"].strip(),
        })
    return problems


def _clean(text):
    """Strip GSM8K calculator annotations like <<16-3-4=9>> for the narrative."""
    text = re.sub(r"<<[^>]*>>", "", text)
    text = re.sub(r"####\s*\S+\s*$", "", text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _condense_question(q):
    """Take the first sentence of the question as a compact summary."""
    first = re.split(r"(?<=[.?!])\s+", q.strip(), maxsplit=1)[0]
    return first


def _final_answer(a):
    """Extract the final numeric answer after the GSM8K '####' marker."""
    m = re.search(r"####\s*(\S+)", a)
    return m.group(1) if m else "?"


def render_narrative(problems):
    """Flatten the five GSM8K problems into a single narrative string.

    One sentence per question, one sentence per answer trace. Keeps the
    final numeric answer so the narrative carries the benchmark signal
    without ballooning past the target range.
    """
    parts = []
    for p in problems:
        q = _clean(p["question"])
        a = _clean(p["answer"])
        ans = _final_answer(p["answer"])
        parts.append(f"Problem {p['idx']} asks {_condense_question(q)}")
        parts.append(f"The reference solution reaches the final answer {ans}.")
    return " ".join(parts)


def main():
    problems = pull_problems(n=5)
    narrative = render_narrative(problems)
    come_trace = come_run(narrative)

    artifact = {
        "benchmark": "gsm8k",
        "split": "test",
        "config": "main",
        "problems": problems,
        "narrative": narrative,
        "come_result": come_trace["result"],
        "stats": {
            "problem_count": len(problems),
            "narrative_chars": len(narrative),
            "opencog_tokens": len(come_trace["opencog_tokens"]),
            "narsese_statements": len(come_trace["narsese_in"]),
            "nars_raw_lines": len(come_trace["nars_inferences"]),
            "derived_inferences": come_trace["result"]["stats"]["count"],
            "mean_confidence": come_trace["result"]["stats"]["mean_conf"],
        },
    }

    out = HERE / "gsm8k_cross_trace.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2, ensure_ascii=False)

    stats = artifact["stats"]
    print(f"gsm8k problems:     {stats['problem_count']}")
    print(f"narrative chars:    {stats['narrative_chars']}")
    print(f"opencog tokens:     {stats['opencog_tokens']}")
    print(f"narsese statements: {stats['narsese_statements']}")
    print(f"derived inferences: {stats['derived_inferences']}")
    print(f"mean confidence:    {stats['mean_confidence']:.4f}")
    print(f"trace written to:   {out}")


if __name__ == "__main__":
    main()
