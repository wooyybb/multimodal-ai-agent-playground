# Dynamic Planning v4.1

## Why Dynamic Planning?

The original pipeline used a fixed execution order. That is stable, but it makes the Planning Agent look less agentic because it cannot explain which tools are needed for a specific request.

v4.1 adds constrained dynamic planning. The Planning Agent can produce a JSON tool plan from the current state and the allowlisted Tool Catalog. The plan is validated before execution, then converted back into the existing execution tool names.

## Tool Catalog

`registry/tool_catalog.py` is the only list exposed to the planner. It contains public aliases, descriptions, required state, produced state, allowed phases, and cost. The LLM never sees raw Python callables, shell access, file deletion tools, or arbitrary registry internals.

Example aliases:

- `understand_reference`
- `parse_reference`
- `build_character_program`
- `compile_semantic_prompt`
- `render_provider_prompt`
- `generate_sdxl_img2img`
- `aggregate_evaluation`
- `analyze_failure`
- `adjust_generation_strategy`

## Plan Schema

The planner must return this structure:

```json
{
  "goal": "",
  "selected_strategy": "",
  "steps": [
    {
      "step_id": 1,
      "tool": "",
      "reason": "",
      "required_state": [],
      "expected_output": [],
      "arguments": {}
    }
  ],
  "stop_conditions": ["generation_success", "evaluation_threshold_met"],
  "max_steps": 12,
  "confidence": 0.0
}
```

The plan is data only. It is not a prompt, code, or direct function call.

## Plan Validation

`workflow/plan_validator.py` checks that:

- every selected tool exists in the Tool Catalog
- the tool is allowed in the current phase
- max step limits are respected
- generation does not run before prompt rendering
- evaluation does not run before generation
- duplicate tools are skipped with warnings
- forbidden tool names such as shell/eval/delete are blocked

Invalid plans fall back to the rule-based plan.

## Rule Fallback

`LLM_PROVIDER=rule` is the default. It returns a safe full workflow plan that preserves the existing SDXL Img2Img, IP-Adapter, ControlNet, evaluation, reflection, and retry flow.

If `LLM_PROVIDER=openai` is selected without `OPENAI_API_KEY`, the planner records fallback metadata and uses the same rule plan.

## Bounded Replanning

Reflection can record a bounded replan when evaluation fails. The current limit is one replan by default. Allowed changes are generation strategy adjustments such as SDXL strength, IP-Adapter scale, ControlNet scale, style strength, provider prompt recompilation, generation rerun, and evaluation rerun.

The system does not allow unlimited retry, tool creation, model installation, arbitrary file edits, or shell execution.

## Agent Safety Constraints

This project is a constrained multimodal agentic workflow, not a fully autonomous system. Safety comes from:

- allowlisted Tool Catalog
- JSON-only tool plan schema
- Plan Validator
- bounded step count
- bounded replan count
- rule fallback
- observable state transitions

## Example Tool Plan

```json
{
  "goal": "Create a reference-aware anime style transfer",
  "selected_strategy": "preserve identity and restyle with SDXL",
  "steps": [
    {"step_id": 1, "tool": "parse_requirement", "reason": "Structure the user request", "required_state": ["user_prompt"], "expected_output": ["style_transfer_program"], "arguments": {}},
    {"step_id": 2, "tool": "understand_reference", "reason": "Analyze the reference image", "required_state": ["image"], "expected_output": ["vision_result"], "arguments": {}},
    {"step_id": 3, "tool": "render_provider_prompt", "reason": "Create provider-specific prompts", "required_state": ["semantic_prompt_program"], "expected_output": ["provider_prompt"], "arguments": {}},
    {"step_id": 4, "tool": "generate_sdxl_img2img", "reason": "Run reference-aware generation", "required_state": ["provider_prompt"], "expected_output": ["output_image_path"], "arguments": {}},
    {"step_id": 5, "tool": "aggregate_evaluation", "reason": "Score the result", "required_state": ["output_image_path"], "expected_output": ["evaluation_result"], "arguments": {}}
  ],
  "stop_conditions": ["generation_success", "evaluation_threshold_met"],
  "max_steps": 12,
  "confidence": 0.82
}
```

## Example Failure And Replan

If evaluation reports weak identity preservation, Reflection can request a bounded adjustment such as increasing IP-Adapter scale or reducing SDXL strength, then rerun generation and evaluation once. The debug report records `replan_count`, `replan_reason`, and `final_stop_condition`.

## Engineering Review

1. Dynamic Planning differs from the old fixed workflow by allowing PlanningAgent to explain selected tools while still mapping back to the same execution engine.
2. Tool Catalog is needed because LLMs must not see raw registry internals or unsafe capabilities.
3. Plan Validator is needed because LLM output is advisory until checked against schema, allowlist, ordering, and step limits.
4. LLM failure falls back to the rule plan, so the workflow does not crash when an API key is missing or JSON parsing fails.
5. Bounded replanning keeps adaptive behavior inspectable and prevents runaway loops.
6. Reference-aware style transfer stays central: planning chooses tools around understanding, prompt rendering, SDXL/IP-Adapter/ControlNet generation, evaluation, and reflection.
7. This is best described as a constrained multimodal agentic workflow with observable tool planning, not a fully autonomous open-ended agent.
8. Not implemented: arbitrary tool discovery, autonomous code execution, model installation, long-horizon memory, and unrestricted multi-step self-modification.
