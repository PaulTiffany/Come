"""
OpenCog learn subprocess wrapper. Mock implementation.

Mock mode returns canonical tokenizer outputs from `mocks/opencog/responses.json`,
keyed by input sentence. Unknown inputs fall back to a documented
whitespace split with a printed warning so the pipeline stays usable in
prototype mode.

Live mode (future) will exec a Dockerized `opencog/learn` via `docker exec`
and pipe a sentence to the tokenizer. The function signature does not change.
"""

import json
import pathlib
import sys
from typing import List


_MOCKS_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "mocks" / "opencog" / "responses.json"
)


def _load_mocks():
    with _MOCKS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def run(sentence: str) -> List[str]:
    """Return a token list for the given sentence.

    In mock mode this is a cache lookup. In live mode this will dispatch
    to the real OpenCog tokenizer.
    """
    mocks = _load_mocks()
    if sentence in mocks:
        return list(mocks[sentence])
    print(
        f"[opencog mock] no cached response for {sentence!r}, "
        f"falling back to whitespace split",
        file=sys.stderr,
    )
    return ["###LEFT-WALL###"] + sentence.split()
