"""
Asserts the adapter functions match their hand-judged oracle fixtures.
"""

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from come.adapters import inferences_to_result, tokens_to_narsese  # noqa: E402


FIXTURE_PATH = pathlib.Path(__file__).resolve().parent / "adapter_fixtures.json"


def _load():
    with FIXTURE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


FIXTURES = _load()


@pytest.mark.parametrize(
    "fixture",
    FIXTURES["tokens_to_narsese"],
    ids=[f["id"] for f in FIXTURES["tokens_to_narsese"]],
)
def test_tokens_to_narsese(fixture):
    actual = tokens_to_narsese(fixture["input"])
    assert actual == fixture["expected"], (
        f"tokens_to_narsese diverged on fixture '{fixture['id']}'.\n"
        f"  rationale: {fixture['rationale']}\n"
        f"  input:     {fixture['input']!r}\n"
        f"  expected:  {fixture['expected']!r}\n"
        f"  actual:    {actual!r}"
    )


@pytest.mark.parametrize(
    "fixture",
    FIXTURES["inferences_to_result"],
    ids=[f["id"] for f in FIXTURES["inferences_to_result"]],
)
def test_inferences_to_result(fixture):
    actual = inferences_to_result(fixture["input"])
    assert actual == fixture["expected"], (
        f"inferences_to_result diverged on fixture '{fixture['id']}'.\n"
        f"  rationale: {fixture['rationale']}\n"
        f"  input:     {fixture['input']!r}\n"
        f"  expected:  {fixture['expected']!r}\n"
        f"  actual:    {actual!r}"
    )
