"""
Adapter functions between the OpenCog and ONA stages of the pipeline.

These are the only first-party functions in the integration. They are what
`mutmut` is pointed at. Every surviving mutant is a hole in either the
oracle fixtures or the adapter behavior.

Two adapters ship today:

  tokens_to_narsese: OpenCog token list -> list of Narsese statements
  inferences_to_result: ONA inference output -> structured result dict
"""

import re
from typing import Dict, List


LEFT_WALL = "###LEFT-WALL###"


def _is_word(token: str) -> bool:
    """A token counts as a word if it contains at least one alphanumeric character.

    The OpenCog tokenizer emits a left wall and punctuation tokens alongside
    real words. We want only real words for adjacency encoding.
    """
    if token == LEFT_WALL:
        return False
    for ch in token:
        if ch.isalnum():
            return True
    return False


def tokens_to_narsese(tokens: List[str]) -> List[str]:
    """Encode adjacent word pairs as Narsese 'follows' statements.

    Example:
        input:  ["###LEFT-WALL###", "the", "cat", "sat", "."]
        output: ['<(*, "the", "cat") --> follows>.',
                 '<(*, "cat", "sat") --> follows>.']
    """
    words = [t for t in tokens if _is_word(t)]
    statements = []
    for i in range(len(words) - 1):
        left = words[i]
        right = words[i + 1]
        statements.append(f'<(*, "{left}", "{right}") --> follows>.')
    return statements


# Compact mock format used by come/nars.py mock mode:
#   <(*, "the", "cat") --> follows>. %1.00;0.90%
_MOCK_RE = re.compile(
    r'^(?P<statement><.+?>\.)\s*%(?P<freq>[01]\.\d+);(?P<conf>[01]\.\d+)%\s*$'
)

# Real ONA output format observed from `./NAR shell`:
#   Derived: <(*, "a", "b") --> follows>. Priority=0.407 Stamp=[2,1] Truth: frequency=1.000000, confidence=0.810000
# The "kind" prefix is Input (echo of the input statement), Selected (internal
# scheduling), or Derived (new inference). Only Derived lines represent new
# knowledge produced by the reasoner. Input and Selected are filtered out.
_ONA_RE = re.compile(
    r'^(?P<kind>Derived|Input|Selected):\s+(?P<statement><.+?>\.)\s+'
    r'Priority=[\d.]+\s+Stamp=\[[\d,\s]+\]\s+Truth:\s+'
    r'frequency=(?P<freq>[\d.]+),\s+confidence=(?P<conf>[\d.]+)\s*$'
)


def _parse_line(line: str):
    """Return (statement, freq, conf) or None.

    Tries the mock format first since it is the simpler match. Falls back to
    real ONA format. For real ONA, only Derived lines are kept.
    """
    line = line.strip()
    m = _MOCK_RE.match(line)
    if m is not None:
        return m.group("statement"), float(m.group("freq")), float(m.group("conf"))
    m = _ONA_RE.match(line)
    if m is not None and m.group("kind") == "Derived":
        return m.group("statement"), float(m.group("freq")), float(m.group("conf"))
    return None


def inferences_to_result(inferences: List[str]) -> Dict:
    """Parse inference lines into a structured result.

    Accepts both the compact mock format `<statement>. %freq;conf%` and the
    real ONA output format with Priority/Stamp/Truth fields. For real ONA
    input, only Derived lines are counted (Input echoes and Selected internal
    scheduling are dropped).

    Returns a dict with:
        statements: list of {"statement", "freq", "conf"}
        stats:      {"count", "mean_freq", "mean_conf"} where means are over
                    successfully parsed lines (0.0 each if count == 0).
    """
    parsed = []
    for line in inferences:
        result = _parse_line(line)
        if result is None:
            continue
        statement, freq, conf = result
        parsed.append({
            "statement": statement,
            "freq": freq,
            "conf": conf,
        })

    count = len(parsed)
    if count == 0:
        mean_freq = 0.0
        mean_conf = 0.0
    else:
        mean_freq = sum(p["freq"] for p in parsed) / count
        mean_conf = sum(p["conf"] for p in parsed) / count

    return {
        "statements": parsed,
        "stats": {
            "count": count,
            "mean_freq": mean_freq,
            "mean_conf": mean_conf,
        },
    }
