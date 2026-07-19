from modules.planning.goal_planner import GoalPlanner
from modules.planning.llm_context_reasoner import LLMContextReasoner
from llm.requirement_parser import RequirementParser
from llm.tool_planner import ToolPlanner
from registry.tool_catalog import ToolCatalog
from workflow.plan_validator import PlanValidator


class PlanningAgent:
    MODULE_SLOTS = {
        "requirement_parser": {
            "status": "active",
            "responsibility": "parse long user requirements into Style Transfer Program JSON",
        },
        "dynamic_tool_planner": {
            "status": "active",
            "responsibility": "select allowlisted tools and build a bounded execution plan",
        },
    }

    def run(self, user_prompt: str, image_provided: bool) -> dict:
        print("[Planning Agent] Running PlanningAgent...")
        requirement_result = RequirementParser().parse(
            {
                "user_prompt": user_prompt,
                "image_provided": image_provided,
            }
        )
        context_reasoning = LLMContextReasoner().run(
            {
                "user_prompt": user_prompt,
                "image_provided": image_provided,
            }
        ).get("context_reasoning")
        goal_tree = GoalPlanner().run(
            {
                "user_prompt": user_prompt,
                "image_provided": image_provided,
            }
        ).get("goal_tree")

        print("[Planning Agent] Building dynamic tool plan...")
        dynamic_plan = self._build_dynamic_tool_plan(
            user_prompt=user_prompt,
            image_provided=image_provided,
            requirement_result=requirement_result,
            goal_tree=goal_tree,
            context_reasoning=context_reasoning,
        )
        execution_plan = dynamic_plan["execution_plan"]
        print(f"[Planning Agent] Selected tools: {dynamic_plan['selected_tools']}")
        print(
            "[Planning Agent] Plan validation: "
            f"{dynamic_plan['plan_validation_result'].get('valid')}"
        )

        result = {
            "task_type": (
                "multi_character_image_generation"
                if self._has_multi_character_hint(user_prompt)
                else "image_generation"
            ),
            "requires_vision": image_provided,
            "requires_generation": True,
            "requires_evaluation": True,
            "requires_retry": True,
            "execution_plan": execution_plan,
            "reason": self._build_reason(user_prompt, image_provided),
            "planning_mode": dynamic_plan.get("planning_mode"),
            "llm_tool_planner_enabled": dynamic_plan.get(
                "llm_tool_planner_enabled", False
            ),
            "tool_plan": dynamic_plan.get("tool_plan"),
            "plan_validation_result": dynamic_plan.get("plan_validation_result"),
            "selected_tools": dynamic_plan.get("selected_tools"),
            "planner_used_fallback": dynamic_plan.get("planner_used_fallback"),
            "planner_fallback_reason": dynamic_plan.get("planner_fallback_reason"),
            "tool_planner_raw_text": dynamic_plan.get("tool_planner_raw_text"),
            "context_reasoning": context_reasoning,
            "goal_tree": goal_tree,
            "requirement_parser_slot": self._prepare_requirement_parser_context(
                user_prompt=user_prompt,
                image_provided=image_provided,
                requirement_result=requirement_result,
            ),
            "style_transfer_program": requirement_result.get("style_transfer_program"),
            "requirement_parser": requirement_result.get("requirement_parser"),
            "parser_provider": requirement_result.get("parser_provider"),
            "parser_used_fallback": requirement_result.get("parser_used_fallback"),
            "parser_error": requirement_result.get("parser_error"),
            "llm_raw_text": requirement_result.get("llm_raw_text"),
            "reasoning_summary": requirement_result.get("reasoning_summary"),
        }

        print(f"[Planning Agent] Execution plan: {execution_plan}")
        return result

    def _build_dynamic_tool_plan(
        self,
        *,
        user_prompt,
        image_provided,
        requirement_result,
        goal_tree,
        context_reasoning,
    ):
        catalog = ToolCatalog()
        planner_payload = {
            "user_prompt": user_prompt,
            "image_provided": image_provided,
            "style_transfer_program": requirement_result.get(
                "style_transfer_program"
            ),
            "parser_provider": requirement_result.get("parser_provider"),
            "parser_used_fallback": requirement_result.get("parser_used_fallback"),
            "goal_tree": goal_tree,
            "context_reasoning": context_reasoning,
            "generation_provider": "runtime_selected",
            "ip_adapter": "optional",
            "controlnet": "optional",
            "previous_evaluation_result": None,
        }
        planner_result = ToolPlanner().plan(
            planner_payload,
            catalog.tools_for_llm(replan=False),
        )
        validation = PlanValidator(catalog).validate(
            planner_result.get("tool_plan"),
            {
                "user_prompt": user_prompt,
                "image": image_provided,
                "style_transfer_program": requirement_result.get(
                    "style_transfer_program"
                ),
            },
            replan=False,
        )

        if validation.get("valid"):
            execution_plan = validation.get("execution_plan") or self._rule_execution_plan()
            planner_used_fallback = bool(planner_result.get("planner_used_fallback"))
            fallback_reason = planner_result.get("planner_fallback_reason", "")
        else:
            execution_plan = self._rule_execution_plan()
            planner_used_fallback = True
            fallback_reason = "; ".join(validation.get("errors") or [])

        return {
            "execution_plan": execution_plan,
            "tool_plan": planner_result.get("tool_plan"),
            "plan_validation_result": validation,
            "selected_tools": validation.get("selected_tools", []),
            "planning_mode": planner_result.get("planning_mode", "rule"),
            "llm_tool_planner_enabled": planner_result.get(
                "llm_tool_planner_enabled", False
            ),
            "planner_used_fallback": planner_used_fallback,
            "planner_fallback_reason": fallback_reason,
            "tool_planner_raw_text": planner_result.get("tool_planner_raw_text"),
        }

    def _rule_execution_plan(self):
        return [
            "goal_planner",
            "memory_load",
            "vision",
            "reference_image_parser",
            "character_program_builder",
            "memory_retrieval",
            "retrieval",
            "prompt_compressor",
            "scene_planning",
            "character",
            "style",
            "layout",
            "pose",
            "expression",
            "lighting",
            "negative_prompt",
            "context_program_builder",
            "context_program_validator",
            "prompt_assembler",
            "prompt_critic",
            "llm_prompt_critic",
            "prompt_optimizer",
            "llm_prompt_optimizer",
            "prompt_compiler",
            "provider_router",
            "provider_prompt_adapter",
            "generation",
            "evaluation",
            "reflection",
            "self_verification",
            "strategy_selector",
            "adaptive_planner",
            "retry",
            "memory_save",
        ]

    def _prepare_requirement_parser_context(
        self,
        user_prompt,
        image_provided,
        requirement_result=None,
    ):
        requirement_result = requirement_result or {}
        return {
            "status": "active",
            "provider": requirement_result.get("parser_provider", "rule"),
            "input_keys": [
                "user_prompt",
                "vision_result",
                "reference_image",
                "character_program",
            ],
            "will_parse_to": "style_transfer_program",
            "llm_call_enabled": requirement_result.get("parser_provider") == "openai",
            "used_fallback": requirement_result.get("parser_used_fallback", True),
            "parser_error": requirement_result.get("parser_error", ""),
            "user_prompt_preview": str(user_prompt or "")[:160],
            "image_provided": bool(image_provided),
        }

    def _build_reason(self, user_prompt, image_provided):
        has_prompt = bool(user_prompt and user_prompt.strip())
        if self._has_multi_character_hint(user_prompt):
            return (
                "Prompt includes possible multi-character reference intent, so "
                "character reference preservation should be considered."
            )

        if image_provided and has_prompt:
            return (
                "Image and prompt are provided, so full multimodal generation "
                "workflow is selected."
            )
        if image_provided:
            return "Image is provided, so vision-based generation workflow is selected."
        if has_prompt:
            return (
                "Prompt is provided without an image, so text-guided generation "
                "workflow is selected."
            )
        return "No specific input is provided, so default generation workflow is selected."

    def _has_multi_character_hint(self, user_prompt):
        text = str(user_prompt or "").lower()
        hints = ("two", "friends", "group", "photobooth", "couple")
        return any(hint in text for hint in hints)


PlannerAgent = PlanningAgent

__all__ = ["PlanningAgent", "PlannerAgent"]
