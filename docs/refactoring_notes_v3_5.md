# Refactoring Notes v3.5

## What Was Cleaned Up

- Orchestrator no longer imports, instantiates, and registers every module directly.
- Tool registration is centralized in `registry/tool_registry_factory.py`.
- Public pipeline result shaping moved to `core/result_builder.py`.
- High-traffic orchestration state key strings moved to `core/state_keys.py`.
- Planning Agent now exposes a clear Requirement Parser slot without adding an LLM call.
- Documentation now describes Orchestrator as a workflow coordinator rather than a sixth agent.

## Why It Was Cleaned Up

The project has grown into a reference-aware style transfer framework. Without cleanup, the code could look like a pile of small agents rather than a designed five-agent system.

v3.5 aligns physical code structure with the public architecture:

```text
Understanding Agent
Planning Agent
Generation Agent
Evaluation Agent
Reflection Agent
```

Small components remain useful, but they are now described and registered as modules inside those responsibilities.

## LLM Requirement Parser Preparation

The next major step is a real Requirement Parser inside the Planning Agent. v3.5 prepares for that by making the boundary explicit:

```text
User Requirement
  |
  v
Planning Agent Requirement Parser Slot
  |
  v
Style Transfer Program
  |
  v
Semantic Prompt Engine / Provider Prompt Compiler
```

No LLM API call is added in this refactor. The current rule/mock behavior remains intact.

## Responsibility Separation

- `OrchestratorAgent`: workflow coordination.
- `ToolRegistryFactory`: module creation and grouped registration.
- `ToolRegistry`: name-to-tool lookup and metadata.
- `DynamicExecutionEngine`: step execution and state update.
- `core/result_builder.py`: public result shape.
- `core/state_keys.py`: shared state key constants.

## Preserved Behavior

- Existing execution plan names.
- Existing ToolRegistry names.
- Existing public result keys.
- Existing SDXL Img2Img/IP-Adapter/ControlNet flow.
- Existing evaluation metrics.
- Existing API/UI/benchmark contracts.

## Remaining Technical Debt

- `DynamicExecutionEngine` is still large and owns many fallback helpers.
- Some state keys are still string literals inside deep workflow code.
- Some prompt responsibilities remain split between `modules/prompt/` and `context/`.
- `ToolRegistry` still performs default registration for a few core tools before the factory registers the full runtime set.
- Interview notes contain older sprint-era content that can be further normalized later.

## Engineering Review

1. Before cleanup, Orchestrator mixed workflow coordination with module construction and registration.
2. After cleanup, Orchestrator coordinates while Registry Factory owns registration.
3. Orchestrator is thinner because result shaping moved to `core/result_builder.py` and state key literals moved to `core/state_keys.py`.
4. Registry Factory provides one place to see which component belongs to which five-agent group.
5. State/Result Builder separation preserves public keys while making the return contract easier to audit.
6. The Planning Agent now has a clear slot where LLM Requirement Parser can be attached later.
7. Remaining debt is mostly ExecutionEngine size and deeper state-key migration.
