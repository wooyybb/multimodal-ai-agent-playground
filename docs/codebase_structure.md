# Codebase Structure v3.5

This document explains the physical code layout after the v3.5 cleanup. The public architecture is still the five-agent model, while implementation details live in modules and core helpers.

## Top-Level Agents

`agents/` contains the application-facing agent entry points:

- `understanding_agent.py`: reference image and visual context ownership.
- `planning_agent.py`: user intent, requirement parser slot, style transfer planning, and execution plan creation.
- `generation_agent.py`: generation-facing high-level boundary.
- `evaluation_agent.py`: evaluation-facing high-level boundary.
- `reflection_agent.py`: reflection and adaptive planning boundary.
- `orchestrator_agent.py`: workflow coordinator, not a sixth agent.

## Modules

`modules/` contains lower-level components that used to look like many small agents:

- `modules/understanding/`: vision, reference parsing, character program building.
- `modules/planning/`: goal, scene, character, style, layout, pose, expression, lighting, context program components.
- `modules/prompt/`: prompt assembly, critique, optimization, compression, and LLM prompt helper modules.
- `modules/generation/`: prompt compiler, provider router, provider adapter, generation request component.
- `modules/evaluation/`: evaluation agent implementation boundary.
- `modules/reflection/`: reflection, strategy, adaptive planning, self-verification, retry.
- `modules/memory/`: memory-related helper modules.

## Core

`core/` collects small cross-cutting framework APIs:

- `state_keys.py`: shared state key constants for high-traffic orchestration fields.
- `result_builder.py`: public pipeline result shape.
- `style_transfer_program.py`: style transfer program facade.
- `semantic_prompt_engine.py`: semantic prompt program facade.
- `reference_conditioning.py`: reference conditioning facade.
- `generation_router.py`: generation routing facade.
- `evaluation_runner.py`: evaluation runner facade.
- `debug_report.py`: debug report facade.

## Context

`context/` owns prompt/context semantics:

- Style Transfer Program schema and helpers.
- Semantic Prompt Program.
- Semantic merge.
- Conflict resolution.
- Prompt sanitizer and validator.
- Provider Prompt Compiler V2.
- Prompt budget optimization.

## Generation and Provider

`generation/` owns generation configuration and routing helpers. `provider/` owns concrete generation provider implementations such as FLUX and SDXL.

The current SDXL path remains SDXL Img2Img with optional IP-Adapter and ControlNet hooks. v3.5 does not add providers or models.

## Evaluation

`evaluation/` owns metrics and aggregation:

- CLIP semantic alignment.
- DINO identity consistency.
- Prompt consistency.
- Aesthetic heuristic.
- Evaluation aggregation and stable score schema.

v3.5 does not add metrics.

## Registry and Workflow

`registry/` separates tool naming from concrete module instances:

- `tool_registry.py`: runtime registry and metadata lookup.
- `tool_registry_factory.py`: grouped construction and registration of tools.

`workflow/` owns execution:

- `execution_engine.py`: runs the planner execution plan step by step.
- `agent_state.py`: shared state validation.
- `debug_report.py`: report and prompt preview writing.
- `pipeline.py`: pipeline support.

## Infrastructure

`memory/`, `api/`, `ui/`, `benchmark/`, and `docs/` remain infrastructure around the same core workflow.

## Rule of Thumb

If a file decides high-level responsibility, it belongs near `agents/`. If it performs one small function, it belongs in `modules/`, `context/`, `generation/`, `provider/`, or `evaluation/`. If it is shared framework glue, it belongs in `core/`, `registry/`, or `workflow/`.
