"""
Cross-run: Microsoft AutoGen multi-agent conversation through the Come pipeline.

Standing with benchmarks, not against. The output of one repository's code
becomes the input of the other's. Reproducible with `pip install pyautogen`
(which pulls in autogen-agentchat and autogen-core).

No external API keys are required. A minimal mock ChatCompletionClient
returns canned strings so the multi-agent loop runs deterministically.
"""

import asyncio
import json
import pathlib
import sys

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.models import (
    ChatCompletionClient,
    CreateResult,
    ModelInfo,
    RequestUsage,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from come.pipeline import run as come_run  # noqa: E402


HERE = pathlib.Path(__file__).resolve().parent


class MockChatCompletionClient(ChatCompletionClient):
    """Minimal AutoGen ChatCompletionClient that returns canned strings.

    Deterministic, no network, no API key. Each call to create returns the
    next canned line and wraps it in the AutoGen CreateResult contract.
    """

    def __init__(self, canned):
        self._canned = list(canned)
        self._idx = 0
        self._total = RequestUsage(prompt_tokens=0, completion_tokens=0)
        self._actual = RequestUsage(prompt_tokens=0, completion_tokens=0)

    async def create(self, messages, *, tools=(), tool_choice="auto",
                     json_output=None, extra_create_args=None,
                     cancellation_token=None):
        text = self._canned[self._idx % len(self._canned)]
        self._idx += 1
        usage = RequestUsage(
            prompt_tokens=len(messages),
            completion_tokens=len(text.split()),
        )
        return CreateResult(
            finish_reason="stop",
            content=text,
            usage=usage,
            cached=False,
        )

    async def create_stream(self, *args, **kwargs):
        result = await self.create(*args, **kwargs)
        yield result

    async def close(self):
        return None

    def actual_usage(self):
        return self._actual

    def total_usage(self):
        return self._total

    def count_tokens(self, messages, *, tools=()):
        return sum(len(str(m)) for m in messages)

    def remaining_tokens(self, messages, *, tools=()):
        return 100000

    @property
    def capabilities(self):
        return self.model_info

    @property
    def model_info(self):
        return ModelInfo(
            vision=False,
            function_calling=False,
            json_output=False,
            family="unknown",
            structured_output=False,
        )


SEEKER_LINES = [
    "I notice the room is dim and the light source is unclear.",
    "If we move closer to the window we should see brightness rise.",
    "The brightness did rise so the window is the dominant source.",
]

SKEPTIC_LINES = [
    "Dimness alone does not localize the source. Consider reflections.",
    "Agreed but only if no lamp is on. We should confirm lamps are off.",
    "Confirmed. The window hypothesis is consistent with observation.",
]


async def run_conversation(max_messages=7):
    """Run a Seeker / Skeptic round-robin and return the message transcript."""
    seeker = AssistantAgent(
        name="Seeker",
        model_client=MockChatCompletionClient(SEEKER_LINES),
        system_message="You are Seeker. Propose hypotheses about the light source.",
    )
    skeptic = AssistantAgent(
        name="Skeptic",
        model_client=MockChatCompletionClient(SKEPTIC_LINES),
        system_message="You are Skeptic. Test each hypothesis before accepting it.",
    )
    team = RoundRobinGroupChat(
        [seeker, skeptic],
        termination_condition=MaxMessageTermination(max_messages),
    )
    result = await team.run(task="Where is the light coming from in this room?")

    transcript = []
    for msg in result.messages:
        source = getattr(msg, "source", "user")
        content = getattr(msg, "content", str(msg))
        transcript.append({"agent": source, "text": str(content)})
    return transcript


def render_narrative(transcript):
    """Flatten the conversation into one sentence per agent turn."""
    parts = []
    for turn in transcript:
        parts.append(f"{turn['agent']} said: {turn['text']}")
    return " ".join(parts)


def main():
    transcript = asyncio.run(run_conversation())
    narrative = render_narrative(transcript)
    come_trace = come_run(narrative)

    artifact = {
        "autogen_transcript": transcript,
        "narrative": narrative,
        "come_result": come_trace["result"],
        "stats": {
            "conversation_turns": len(transcript),
            "narrative_chars": len(narrative),
            "opencog_tokens": len(come_trace["opencog_tokens"]),
            "narsese_statements": len(come_trace["narsese_in"]),
            "nars_raw_lines": len(come_trace["nars_inferences"]),
            "derived_inferences": come_trace["result"]["stats"]["count"],
            "mean_confidence": come_trace["result"]["stats"]["mean_conf"],
        },
    }

    out = HERE / "autogen_cross_trace.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    stats = artifact["stats"]
    print(f"conversation turns: {stats['conversation_turns']}")
    print(f"narrative chars:    {stats['narrative_chars']}")
    print(f"opencog tokens:     {stats['opencog_tokens']}")
    print(f"narsese statements: {stats['narsese_statements']}")
    print(f"derived inferences: {stats['derived_inferences']}")
    print(f"mean confidence:    {stats['mean_confidence']:.4f}")
    print(f"trace written to:   {out}")


if __name__ == "__main__":
    main()
