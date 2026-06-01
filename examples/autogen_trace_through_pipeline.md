# AutoGen multi-agent trace through the Come pipeline

A live cross-run demonstrating that Microsoft AutoGen (Wu et al., 2023) and this repository's integration pipeline can be composed end to end. The output of one becomes the input of the other.

This is companion evidence for the AGI-26 paper's Future Work commitment: *"Standing with benchmarks, not against."*

## Pipeline composition

```
AutoGen (autogen-agentchat 0.7.5, RoundRobinGroupChat) -> 2-agent 7-message conversation
  -> narrative renderer (one sentence per agent turn)
    -> Come pipeline
       -> OpenCog tokenize (mock with whitespace fallback)
       -> tokens_to_narsese adapter (mutation-tested)
       -> NARS (mock: echo as facts at confidence 0.90)
       -> inferences_to_result adapter (mutation-tested)
    -> structured derived inferences
```

## Run

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination

seeker = AssistantAgent(name="Seeker", model_client=MockChatCompletionClient(seeker_lines), ...)
skeptic = AssistantAgent(name="Skeptic", model_client=MockChatCompletionClient(skeptic_lines), ...)
team = RoundRobinGroupChat([seeker, skeptic], termination_condition=MaxMessageTermination(7))
result = await team.run(task="Where is the light coming from in this room?")
```

No external LLM API keys are used. A minimal `MockChatCompletionClient` implements the AutoGen `ChatCompletionClient` protocol and returns canned strings, so the multi-agent loop runs deterministically.

The AutoGen conversation is rendered as a sentence per turn:

> "user said: Where is the light coming from in this room? Seeker said: I notice the room is dim and the light source is unclear. Skeptic said: Dimness alone does not localize the source. Consider reflections. Seeker said: If we move closer to the window we should see brightness rise. ..."

Then fed to `come.pipeline.run`.

## Output stats

| Metric | Value |
|---|---|
| Input chars (narrative) | 517 |
| AutoGen conversation turns | 7 |
| OpenCog tokens | 90 |
| Narsese statements emitted | 88 |
| NARS raw lines | 88 |
| Derived inferences (filtered) | 88 |
| Mean confidence | 0.9000 |

## What this is and is not

**Is.** A working composition of Microsoft AutoGen's multi-agent conversation framework and this repository's pipeline. Both codes ran. The output of AutoGen became the input of Come. The integration substrate is real.

**Is not.** A meaningful validation of either system. The AutoGen agents are driven by a mock ChatCompletionClient that returns canned strings, not a live LLM. The narrative renderer is a thin text-flattening of the conversation, not a semantic translation. The Come NARS stage is in mock mode (echo as facts). The 0.90 confidence is the mock confidence, not a measurement of multi-agent reasoning correctness.

**Means.** This is operational integration, not semantic validation. The stats are real but the meaning is that the substrate is real, not that we beat AutoGen on any task. The "Standing with benchmarks, not against" stance in the AGI-26 Future Work paragraph is operational, not aspirational. The cross-pipeline substrate is here today. Deeper integration (real LLM-backed agents and a richer renderer that preserves dialogue structure) is the natural next step.

## Reproduction

1. `pip install pyautogen` (pulls in autogen-agentchat 0.7.5 and autogen-core)
2. `pip install -r requirements.txt && python examples/run_autogen_cross.py`

## Related

- AGI-26 paper Future Work: cites this run via `\cite{tiffany2026come}`.
- AutoGen reference: Wu, Q., Bansal, G., Zhang, J., Wu, Y., Li, B., Zhu, E., Jiang, L., Zhang, X., Zhang, S., Liu, J., Awadallah, A. H., White, R. W., Burger, D., Wang, C. *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation.* arXiv:2308.08155, 2023.
- The PyMDP active-inference trace was previously run through this same pipeline. See `pymdp_trace_through_pipeline.md`.
- The Surface paper abstract was also run through this same pipeline. See `surface_abstract_through_pipeline.md`.
