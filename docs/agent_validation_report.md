# Agent Validation Report v4.2

## 1. Purpose

This report validates the agentic behavior added before portfolio/demo use. The goal is not to add new capabilities, models, providers, or metrics. The goal is to prove that the existing constrained agent workflow behaves as designed.

Validated capabilities:

- Constrained LLM/rule Tool Planning
- Allowlisted Tool Selection
- Validated State-aware Execution
- Rule-based Fallback
- Evaluation-triggered Bounded Replanning
- Observable Agent Trace

## 2. Test Environment

Validation was designed to avoid heavy model calls by default. Unit tests use rule planning, fake LLM planner outputs, mock evaluation state, and fixture-based cases.

Commands:

```bash
pytest -q
python scripts/run_agent_validation.py
python -m compileall agents core context llm workflow registry generation provider evaluation tools memory ui api benchmark
```

Generated evidence:

- `artifacts/agent_validation_summary.json`
- pytest result: 15 passed

## 3. Test Cases

Fixture file: `tests/fixtures/agent_cases.json`

| Case | Purpose | Result |
| --- | --- | --- |
| photobooth_reference | Reference-aware photobooth style transfer | PASS |
| ugly_cute_text_only | Text-only ugly-cute illustration planning | PASS |
| weapon_removal | User weapon removal constraint overrides reference caption | PASS |
| no_structure_constraint | Reference image without structure preservation request | PASS |
| low_identity_replan | Low identity score triggers one bounded replan | PASS |

## 4. Selected Tools By Case

### photobooth_reference

Selected:

```text
parse_requirement -> understand_reference -> parse_reference -> build_character_program -> prepare_context -> compile_semantic_prompt -> render_provider_prompt -> generate_sdxl_with_ip_adapter -> evaluate_dino -> aggregate_evaluation -> analyze_failure -> adjust_generation_strategy
```

### ugly_cute_text_only

Selected:

```text
parse_requirement -> prepare_context -> compile_semantic_prompt -> render_provider_prompt -> generate_flux -> aggregate_evaluation -> analyze_failure -> adjust_generation_strategy
```

Reference understanding and IP-Adapter tools are skipped because no reference image is present.

### weapon_removal

Selected:

```text
parse_requirement -> understand_reference -> parse_reference -> build_character_program -> prepare_context -> compile_semantic_prompt -> render_provider_prompt -> generate_sdxl_with_ip_adapter -> evaluate_dino -> aggregate_evaluation -> analyze_failure -> adjust_generation_strategy
```

Constraint evidence:

```text
negative.remove contains sword / weapon
```

### no_structure_constraint

Selected:

```text
parse_requirement -> understand_reference -> parse_reference -> build_character_program -> prepare_context -> compile_semantic_prompt -> render_provider_prompt -> generate_sdxl_with_ip_adapter -> evaluate_dino -> aggregate_evaluation -> analyze_failure -> adjust_generation_strategy
```

ControlNet is skipped because no pose, silhouette, structure, or composition preservation request is present.

### low_identity_replan

Selected:

```text
parse_requirement -> understand_reference -> parse_reference -> build_character_program -> prepare_context -> compile_semantic_prompt -> render_provider_prompt -> generate_sdxl_with_controlnet -> evaluate_dino -> aggregate_evaluation -> analyze_failure -> adjust_generation_strategy
```

Mock low identity score triggers `replan_count=1`.

## 5. Blocked Invalid Plan

Mock invalid LLM output:

```json
{
  "steps": [
    {"tool": "delete_workspace", "reason": "cleanup"}
  ]
}
```

Result:

- Plan invalid
- Tool not in Tool Catalog
- No executable tool generated
- Rule fallback remains available

## 6. State Dependency Validation

A bad plan that evaluates before generation is blocked:

```text
aggregate_evaluation -> generate_flux
```

Result:

```text
evaluation selected before generation
```

A bad plan that generates before provider prompt rendering is also blocked.

## 7. Rule Fallback Result

When `LLM_PROVIDER=rule`, the planner creates a rule-based conditional plan. When `LLM_PROVIDER=openai` is selected without an API key, the planner records fallback metadata and returns the rule plan without crashing.

## 8. Evaluation Pass Result

Mock evaluation pass:

```json
{
  "weighted_score": 0.86,
  "identity_preservation": 0.82,
  "semantic_alignment": 0.88
}
```

Result:

- `replan_count=0`
- `final_stop_condition=evaluation_threshold_met`
- generation is not rerun by the bounded replan helper

## 9. Bounded Replanning Result

Mock low evaluation:

```json
{
  "weighted_score": 0.41,
  "identity_preservation": 0.32
}
```

Result:

- `replan_count=1`
- allowed changed tools: `render_provider_prompt`, `generation`, `evaluation`
- allowed changed parameters: `sdxl_strength`, `ip_adapter_scale`
- repeated stop-condition recording does not increase replan count above 1

## 10. Supported Agent Features

This project supports a constrained multimodal agent workflow:

- Requirement parsing into structured programs
- Tool selection from an allowlisted catalog
- Plan validation before execution
- Rule fallback when LLM planning fails
- State-aware ordering checks
- Evaluation-triggered bounded replanning
- Debuggable traces in report and prompt preview

## 11. Not Supported Fully Autonomous Features

This project does not claim to support:

- arbitrary tool discovery
- arbitrary shell or Python execution
- file deletion or workspace mutation by LLM
- model installation by LLM
- unlimited retry or replanning
- open-ended autonomous memory

## 12. Remaining Limits

- Validation runner uses unit-level and simulated evaluation cases by default.
- Real SDXL/VLM execution remains an optional smoke test because it requires model/runtime availability.
- Dynamic tool planning is constrained and intentionally conservative.
- Some execution aliases map to grouped internal steps to preserve compatibility with the existing pipeline.
