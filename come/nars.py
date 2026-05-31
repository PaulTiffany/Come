"""
OpenNARS (ONA) subprocess wrapper. Mock and live modes.

Mock mode (default) returns canonical inference outputs from
`mocks/nars/responses.json` keyed by a stable hash of the input statement list.
Unknown inputs fall back to echo-as-fact with confidence 0.90.

Live mode dispatches to a real ONA binary via subprocess. Activated by setting
`COME_NARS_MODE=live` in the environment. Defaults to the WSL2 invocation that
Agent B validated:

    wsl -d Ubuntu -- bash -c "cd ~/ONA && ./NAR shell"

Override with:
    COME_NARS_CMD='<custom shell command that invokes NAR with stdin/stdout>'
    COME_NARS_STEPS=10        (inference steps requested after statements; default 10)
    COME_NARS_TIMEOUT=60      (subprocess timeout in seconds; default 60)
"""

import hashlib
import json
import os
import pathlib
import subprocess
import sys
from typing import List


_MOCKS_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "mocks" / "nars" / "responses.json"
)

_DEFAULT_LIVE_CMD = ["wsl", "-d", "Ubuntu", "--", "bash", "-c", "cd ~/ONA && ./NAR shell"]


def _load_mocks():
    with _MOCKS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _key(statements: List[str]) -> str:
    h = hashlib.sha256()
    for s in statements:
        h.update(s.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def _run_live(statements: List[str]) -> List[str]:
    """Pipe statements into a real ONA binary and collect stdout lines.

    Protocol: write each Narsese statement on its own line, then a step
    count (an integer), then quit. The ONA shell processes statements,
    runs the requested number of inference steps, and exits.
    """
    cmd_str = os.environ.get("COME_NARS_CMD")
    if cmd_str:
        cmd = ["sh", "-c", cmd_str] if os.name != "nt" else ["cmd", "/c", cmd_str]
    else:
        cmd = _DEFAULT_LIVE_CMD

    steps = os.environ.get("COME_NARS_STEPS", "10")
    timeout = int(os.environ.get("COME_NARS_TIMEOUT", "60"))

    stdin_text = "\n".join(statements + [str(steps), "quit"]) + "\n"

    try:
        result = subprocess.run(
            cmd,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as e:
        print(
            f"[nars live] subprocess command not found: {e}. "
            f"Falling back to mock-echo. "
            f"Verify WSL availability or set COME_NARS_CMD.",
            file=sys.stderr,
        )
        return [f"{s} %1.00;0.90%" for s in statements]
    except subprocess.TimeoutExpired:
        print(
            f"[nars live] subprocess timed out after {timeout}s. "
            f"Falling back to mock-echo.",
            file=sys.stderr,
        )
        return [f"{s} %1.00;0.90%" for s in statements]

    if result.returncode != 0:
        print(
            f"[nars live] subprocess exited {result.returncode}. "
            f"stderr: {result.stderr[:500]}",
            file=sys.stderr,
        )

    return [line for line in result.stdout.splitlines() if line.strip()]


def run(statements: List[str]) -> List[str]:
    """Return inference lines for the given Narsese input.

    Mock mode (default) returns lines in the compact format `<stmt>. %freq;conf%`.
    Live mode returns real ONA output in the format
        Derived: <stmt>. Priority=N Stamp=[...] Truth: frequency=N, confidence=N

    The downstream adapter `inferences_to_result` handles both formats.
    """
    mode = os.environ.get("COME_NARS_MODE", "mock").lower()
    if mode == "live":
        return _run_live(statements)

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
