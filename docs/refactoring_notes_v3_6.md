# Refactoring Notes v3.6

## Goal

v3.6 is a code diet refactor. It does not add features, models, providers, metrics, or generation behavior. The goal is to reduce small-file fragmentation while preserving the existing reference-aware style transfer workflow.

## Deleted / Consolidated Files

The Evaluation Layer had one file per small metric. These were consolidated into `evaluation/metrics.py`:

- `evaluation/metric_base.py`
- `evaluation/clip_metric.py`
- `evaluation/dino_metric.py`
- `evaluation/identity_metric.py`
- `evaluation/prompt_metric.py`
- `evaluation/aesthetic_metric.py`

Replacement:

- `evaluation/metrics.py`

Net effect: six metric files became one metric module.

## Kept Core Files

- `agents/orchestrator_agent.py`: workflow coordinator.
- `agents/planning_agent.py`: execution planning and Requirement Parser slot.
- `registry/tool_registry_factory.py`: grouped tool registration.
- `workflow/execution_engine.py`: planned step execution.
- `core/state_keys.py`: high-traffic orchestration state keys.
- `core/result_builder.py`: public pipeline result shape.
- `evaluation/evaluation_aggregator.py`: metric execution, weights, fallback, result schema.
- `evaluation/metrics.py`: concrete metric implementations.

## Consolidation Criteria

Files were merged when they met these conditions:

- The file only contained a small class with no independent runtime boundary.
- The implementation was only imported by the evaluation aggregator/core facade.
- The code belonged to the same responsibility: metric evaluation.
- Merging did not change public state keys, metric names, scores, or weights.

## Preserved Behavior

- CLIP metric still uses prompt-image semantic alignment.
- DINO metric still performs reference-generated image similarity when available and falls back safely.
- Identity, Prompt, and Aesthetic metrics keep their rule-based scoring.
- EvaluationAggregator keeps the same weights and result schema.
- SDXL Img2Img, IP-Adapter, and ControlNet flows are unchanged.

## Remaining Wrappers

No compatibility wrappers were kept for the deleted metric files because internal imports now point to `evaluation.metrics`. The public evaluation facade remains `core.evaluation_runner`.

## Future Removable Targets

- Some prompt helper modules under `modules/prompt/` can be moved behind `context/semantic_prompt_engine.py` later.
- Planning micro-modules such as style/layout/lighting/pose/expression can be reviewed after execution-plan stability is locked.
- Reflection helpers can eventually be collected behind a single reflection runner.
- `DynamicExecutionEngine` still contains many fallback helpers and can be split carefully later.

## Why This Fits the 5-Agent Architecture

The refactor makes Evaluation read as one responsibility:

```text
Evaluation Agent
  |
  +-- evaluation/metrics.py
  +-- evaluation/evaluation_aggregator.py
```

Instead of exposing many metric files as if they were separate architectural units, the code now shows metrics as components inside the Evaluation Agent boundary.

## Engineering Review

1. Deleted/consolidated files: six evaluation metric files were merged into `evaluation/metrics.py`.
2. Maintained files: Orchestrator, PlanningAgent, RegistryFactory, ExecutionEngine, ResultBuilder, StateKeys, EvaluationAggregator, and Metrics.
3. Criteria: merge small, same-responsibility files with narrow import surface.
4. Function preservation: metric names, result schema, scoring, weights, and fallbacks are unchanged.
5. Wrappers: no metric wrappers remain; internal imports were updated.
6. Future removals: prompt micro-modules, planning micro-modules, reflection helper modules, and some ExecutionEngine fallback helpers.
7. Architecture fit: Evaluation metrics are now components under one Evaluation Layer instead of scattered small files.
