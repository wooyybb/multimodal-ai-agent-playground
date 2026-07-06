# Release Notes v3: Agent Architecture Refactoring

## Focus

v3 clarifies the framework as a **5-Agent Architecture**:

1. Understanding Agent
2. Planning Agent
3. Generation Agent
4. Evaluation Agent
5. Reflection Agent

The goal is explanation quality and architectural clarity, not new functionality.

## What Changed

- README now introduces the project as a reference-aware multimodal AI Agent framework for style transfer.
- Documentation explains small agents as internal modules/components.
- `ToolRegistry` now exposes `agent_group` metadata for components.
- `DynamicExecutionEngine` records executed agent groups and component traces.
- Debug reports include `agent_architecture_version`, `executed_agent_groups`, and `component_trace`.
- `docs/agent_architecture_v3.md` documents the 5-Agent model and Agent vs Module distinction.

## What Did Not Change

- No new generation model was added.
- No new VLM, LLM, metric, API, UI, or benchmark feature was added.
- Existing FLUX, SDXL Img2Img, IP-Adapter hook, ControlNet hook, evaluation, benchmark, FastAPI, and Gradio flows remain unchanged.

## Compatibility

The refactor is documentation and metadata oriented. Existing execution plans still run component-by-component through `DynamicExecutionEngine` and `ToolRegistry`.

## Future Work

- Expose the 5-Agent trace in a UI/debug dashboard.
- Continue consolidating naming from sprint-era modules into stable architecture terms.
