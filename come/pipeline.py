"""
End-to-end pipeline runner.

Usage:
    python -m come.pipeline "the cat sat on the mat"

Prints a numbered trace of every stage. Mock mode is the default.
"""

import json
import sys
from typing import Dict

from come import adapters, nars, opencog


def run(sentence: str) -> Dict:
    """Run the full pipeline and return a dict with every stage's output."""
    tokens = opencog.run(sentence)
    narsese = adapters.tokens_to_narsese(tokens)
    inferences = nars.run(narsese)
    result = adapters.inferences_to_result(inferences)
    return {
        "input": sentence,
        "opencog_tokens": tokens,
        "narsese_in": narsese,
        "nars_inferences": inferences,
        "result": result,
    }


def _print_trace(trace: Dict) -> None:
    print(f'[1] input:      {trace["input"]!r}')
    print(f'[2] opencog:    {trace["opencog_tokens"]}')
    print(f'[3] adapter:    {trace["narsese_in"]}')
    print(f'[4] nars:       {trace["nars_inferences"]}')
    print(f'[5] adapter:    {json.dumps(trace["result"], indent=2)}')


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python -m come.pipeline <sentence>", file=sys.stderr)
        return 2
    sentence = " ".join(sys.argv[1:])
    trace = run(sentence)
    _print_trace(trace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
