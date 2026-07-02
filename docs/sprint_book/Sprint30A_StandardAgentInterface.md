# Sprint 30A: Standard Agent Interface

## Objective

Introduce a standard `run(state: dict) -> dict` interface for selected agents.

## Problem

ExecutionEngine currently knows too much about each agent's argument list. This becomes harder to maintain as agents increase.

## Design Decision

Add `ToolRegistry.run_with_state()` and migrate selected upper-layer agents first.

## Implementation Summary

- Added `run_with_state()` to ToolRegistry.
- Added state-based mode to ScenePlanningAgent, PromptAssembler, PromptCriticAgent, ProviderRouter, and ProviderPromptAdapter.
- Updated ExecutionEngine to call selected steps with state and merge returned updates.
- Preserved existing argument-based calls.

## AI Agent Concept

This Sprint introduces State-based Agent execution and LangGraph-style node thinking without adding an external framework.

## Prompt Engineering Note

The Sprint prompt constrained file scope and explicitly required backward compatibility, making the refactor safer.

## Interview Talking Points

- `run(state) -> dict` reduces argument mapping in ExecutionEngine.
- Incremental migration avoids breaking the E2E workflow.
- A future AgentState schema can make state keys safer.

## Future Work

- Convert remaining agents.
- Add AgentState dataclass.
- Add state validation and richer tracing.
