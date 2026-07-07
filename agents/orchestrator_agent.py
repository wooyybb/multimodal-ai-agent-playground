from agents.planning_agent import PlannerAgent
from registry import build_tool_registry
from workflow.execution_engine import DynamicExecutionEngine


class OrchestratorAgent:
    RESULT_KEYS = (
        "caption",
        "final_prompt",
        "output_image_path",
        "score",
        "retry_needed",
        "retry_output_image_path",
        "retry_score",
        "reflection",
        "suggested_prompt",
        "best_prompt",
        "best_output_image_path",
        "best_score",
        "history_path",
        "last_run",
        "memory_context",
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
        "provider",
        "compiled_prompt_package",
        "provider_prompt",
        "provider_negative_prompt",
        "adapter_notes",
        "prompt_sections",
        "agent_trace",
    )

    def __init__(self):
        self.planner_agent = PlannerAgent()
        self.registry = build_tool_registry()
        self.execution_engine = DynamicExecutionEngine()

    def run(self, image, user_prompt, provider=None):
        print("[OrchestratorAgent] Starting workflow coordination...")
        planner_result = self.planner_agent.run(
            user_prompt=user_prompt,
            image_provided=image is not None,
        )
        state = self._build_initial_state(image, user_prompt, provider, planner_result)
        final_state = self.execution_engine.run(
            planner_result.get("execution_plan", []),
            self.registry,
            state,
        )
        print("[OrchestratorAgent] Workflow coordination finished.")
        return self._build_result(final_state, planner_result)

    def _build_initial_state(self, image, user_prompt, provider, planner_result):
        return {
            "image": image,
            "user_prompt": user_prompt,
            "requested_provider": provider,
            "provider": provider,
            "planner_result": planner_result,
            "agent_trace": ["PlanningAgent generated execution plan"],
        }

    def _build_result(self, final_state, planner_result):
        result = {
            key: final_state.get(key)
            for key in self.RESULT_KEYS
            if key != "agent_trace"
        }
        result["memory_saved"] = final_state.get("memory_saved", False)
        result["planner_result"] = planner_result
        result["agent_trace"] = final_state.get("agent_trace", [])
        return result
