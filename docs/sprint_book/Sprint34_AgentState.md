# Sprint 34: AgentState Framework Core

## Objective

Introduce `AgentState` as the shared framework state object.

## Problem

The project uses plain dict state. As more agents were added, state keys such as `caption`, `scene_plan`, `provider_prompt`, `prompt_report`, and `optimization_report` became harder to manage safely.

## Design Decision

Add a dataclass-based `AgentState` in `workflow/agent_state.py` and use it at ExecutionEngine and ToolRegistry boundaries while preserving the existing dict workflow.

## Implementation Summary

- Added `AgentState`.
- Added `from_dict()`, `to_dict()`, `update_from_dict()`, and `validate()`.
- ExecutionEngine now builds and validates AgentState at start and finish.
- ToolRegistry can run state-based tools with either dict or AgentState.

## AI Agent Concept

AgentState is a framework core primitive for Shared State, Typed State, and State Validation.

## Prompt Engineering Note

The Sprint explicitly forbade Agent edits, so the implementation used a compatibility layer instead of a full refactor.

## Interview Talking Points

- AgentState reduces dict key drift.
- Validation warns without breaking workflow execution.
- Unknown keys are preserved in `extra`.
- This is a foundation for graph state and multi-session execution.

## Future Work

- Convert agents to consume AgentState directly.
- Add stricter schema validation.
- Support graph state and distributed agent execution.
