"""Public pipeline result shaping.

The Orchestrator should coordinate workflow execution, not own a long return
dictionary. This module preserves the existing public result keys while keeping
that shape in one place.
"""

from core import state_keys as keys


PIPELINE_RESULT_KEYS = (
    keys.CAPTION,
    keys.FINAL_PROMPT,
    keys.OUTPUT_IMAGE_PATH,
    keys.SCORE,
    "retry_needed",
    "retry_output_image_path",
    "retry_score",
    "reflection",
    "suggested_prompt",
    "best_prompt",
    "best_output_image_path",
    keys.BEST_SCORE,
    "history_path",
    "last_run",
    "memory_context",
    "memory_saved",
    keys.PLANNER_RESULT,
    "prompt_context",
    "retrieved_context",
    "compressed_context",
    "scene_plan",
    "character_section",
    "style_section",
    "layout_section",
    "pose_section",
    "expression_section",
    "lighting_section",
    "negative_prompt",
    "context_program",
    "context_program_summary",
    "context_program_version",
    "context_validation",
    "canonical_prompt",
    "prompt_report",
    "prompt_quality_score",
    "llm_prompt_critic_report",
    "llm_prompt_critic_score",
    "optimized_prompt",
    "optimization_report",
    "llm_optimized_prompt",
    "llm_optimizer_report",
    "provider_routing",
    keys.PROVIDER,
    "compiled_prompt_package",
    "provider_prompt",
    "provider_negative_prompt",
    "adapter_notes",
    "prompt_sections",
    keys.AGENT_TRACE,
)


def build_pipeline_result(final_state: dict, planner_result: dict) -> dict:
    result = {}
    for key in PIPELINE_RESULT_KEYS:
        if key == "memory_saved":
            result[key] = final_state.get(key, False)
        elif key == keys.PLANNER_RESULT:
            result[key] = planner_result
        elif key == keys.AGENT_TRACE:
            result[key] = final_state.get(key, [])
        else:
            result[key] = final_state.get(key)
    return result
