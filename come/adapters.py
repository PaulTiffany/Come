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


# Matches an ONA-style line:
#   <(*, "the", "cat") --> follows>. %1.00;0.90%
# Captures: statement (everything up to and including the period), freq, conf.
_INFERENCE_RE = re.compile(
    r'^(?P<statement><.+?>\.)\s*%(?P<freq>[01]\.\d+);(?P<conf>[01]\.\d+)%\s*$'
)


def inferences_to_result(inferences: List[str]) -> Dict:
    """Parse ONA inference lines into a structured result.

    Each line is expected to be of the form:
        <statement>. %freq;conf%

    Returns a dict with:
        statements: list of {"statement", "freq", "conf"}
        stats:      {"count", "mean_freq", "mean_conf"} where means are over
                    successfully parsed lines (0.0 each if count == 0).
    """
    parsed = []
    for line in inferences:
        m = _INFERENCE_RE.match(line.strip())
        if m is None:
            continue
        parsed.append({
            "statement": m.group("statement"),
            "freq": float(m.group("freq")),
            "conf": float(m.group("conf")),
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
