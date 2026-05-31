"""
OpenNARS (ONA) subprocess wrapper. Mock implementation.

Mock mode returns canonical inference outputs from `mocks/nars/responses.json`.
The mock keys responses by a stable hash of the input statement list, so the
same input always yields the same output.

Live mode (future) will exec a Dockerized ONA, pipe Narsese on stdin, and
collect inferences on stdout. The function signature does not change.
"""

import hashlib
import json
import pathlib
import sys
from typing import List


_MOCKS_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "mocks" / "nars" / "responses.json"
)


def _load_mocks():
    with _MOCKS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _key(statements: List[str]) -> str:
    h = hashlib.sha256()
    for s in statements:
        h.update(s.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def run(statements: List[str]) -> List[str]:
    """Return inference lines for the given Narsese input.

    Each output line is of the form:
        <statement>. %freq;conf%

    In mock mode this is a cache lookup. In live mode this will dispatch
    to ONA via subprocess.
    """
    mocks = _load_mocks()
    key = _key(statements)
    if key in mocks:
        return list(mocks[key])
    print(
        f"[nars mock] no cached response for input hash {key[:12]}..., "
        f"echoing inputs as facts with %1.00;0.90%",
        file=sys.stderr,
    )
    return [f"{s} %1.00;0.90%" for s in statements]
