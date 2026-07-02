# Sprint 30A: Standard Agent Interface

## Problem

As more agents are added, ExecutionEngine has to manage step-specific argument mapping directly. This makes the workflow harder to extend.

## Decision

Start migrating selected upper-layer agents to `run(state) -> dict` and add `ToolRegistry.run_with_state()`.

## Alternatives

- Keep the mixed interface.
- Convert every agent in one Sprint.
- Introduce `AgentState` dataclass immediately.
- Replace the custom workflow with LangGraph.

## Reason

Incremental refactoring improves the architecture while preserving the existing E2E workflow. Backward compatibility keeps direct calls and older step handlers working.

## Future Work

- Convert all agents to the standard state interface.
- Add `AgentState` dataclass or schema validation.
- Expand toward a LangGraph-style node graph if needed.
