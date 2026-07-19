from core.tool_plan_schema import ToolPlanSchema
from llm.openai_reasoner import dumps_payload
from llm.reasoner_router import ReasonerRouter


class ToolPlanner:
    def __init__(self, provider=None):
        self.router = ReasonerRouter(provider)

    def plan(self, payload, tool_catalog):
        fallback_plan = self._rule_plan_from_payload(payload)
        provider = self.router.provider
        if provider in ("rule", "mock", "none", ""):
            return self._finish(
                fallback_plan,
                provider,
                used_fallback=True,
                reason="rule planner selected",
            )

        system_prompt = (
            "You are a constrained dynamic tool planner. "
            "Return JSON only. Select tools only from the provided Tool Catalog. "
            "Do not write final prompts, code, shell commands, eval calls, or file operations. "
            "Use the schema: goal, selected_strategy, steps, stop_conditions, max_steps, confidence."
        )
        user_prompt = dumps_payload(
            {
                "state_summary": payload,
                "tool_catalog": tool_catalog,
                "max_steps": ToolPlanSchema.DEFAULT_MAX_STEPS,
            }
        )
        result = self.router.reason(
            system_prompt,
            user_prompt,
            fallback=fallback_plan,
            schema_name="dynamic_tool_plan",
        )
        used_fallback = bool(result.get("reasoning_used_fallback"))
        plan = ToolPlanSchema.normalize(result, fallback_goal=fallback_plan["goal"])
        return self._finish(
            plan,
            provider,
            used_fallback=used_fallback,
            reason=result.get("reasoning_fallback_reason", ""),
            raw_text=result.get("llm_reasoning_raw_text"),
        )

    def _rule_plan_from_payload(self, payload):
        payload = payload or {}
        text = str(payload.get("user_prompt") or "")
        lowered = text.lower()
        image_provided = bool(payload.get("image_provided"))
        style_program = payload.get("style_transfer_program") or {}
        strategy = style_program.get("generation_strategy") or {}

        steps = [
            self._step(1, "parse_requirement", "Structure the user requirement."),
        ]
        step_id = 2
        if image_provided:
            for tool, reason in (
                ("understand_reference", "Analyze the reference image."),
                ("parse_reference", "Extract structured reference context."),
                ("build_character_program", "Build identity and appearance constraints."),
            ):
                steps.append(self._step(step_id, tool, reason))
                step_id += 1

        steps.append(
            self._step(step_id, "prepare_context", "Build planning and context modules.")
        )
        step_id += 1
        steps.append(
            self._step(step_id, "compile_semantic_prompt", "Compile semantic prompt program.")
        )
        step_id += 1
        steps.append(
            self._step(step_id, "render_provider_prompt", "Render provider-specific prompt.")
        )
        step_id += 1

        generation_tool = "generate_flux"
        if image_provided:
            generation_tool = "generate_sdxl_img2img"
            if strategy.get("use_controlnet") or self._has_structure_request(lowered):
                generation_tool = "generate_sdxl_with_controlnet"
            elif strategy.get("use_ip_adapter") or self._has_identity_request(lowered):
                generation_tool = "generate_sdxl_with_ip_adapter"
        steps.append(self._step(step_id, generation_tool, "Run selected generation route."))
        step_id += 1

        if image_provided and self._has_identity_request(lowered):
            steps.append(self._step(step_id, "evaluate_dino", "Check visual identity consistency."))
            step_id += 1
        steps.append(self._step(step_id, "aggregate_evaluation", "Aggregate evaluation metrics."))
        step_id += 1
        steps.append(self._step(step_id, "analyze_failure", "Analyze quality and failure type."))
        step_id += 1
        steps.append(
            self._step(step_id, "adjust_generation_strategy", "Apply bounded replanning if needed.")
        )

        return ToolPlanSchema.normalize(
            {
                "goal": text or "Reference-aware style transfer",
                "selected_strategy": "rule_conditional_tool_selection",
                "steps": steps,
                "max_steps": ToolPlanSchema.DEFAULT_MAX_STEPS,
                "confidence": 0.74,
            }
        )

    def _step(self, step_id, tool, reason):
        return {
            "step_id": step_id,
            "tool": tool,
            "reason": reason,
            "required_state": [],
            "expected_output": [],
            "arguments": {},
        }

    def _has_identity_request(self, lowered):
        return any(
            token in lowered
            for token in (
                "identity",
                "preserve",
                "same person",
                "face",
                "hair",
                "outfit",
                "reference",
            )
        )

    def _has_structure_request(self, lowered):
        return any(
            token in lowered
            for token in (
                "pose",
                "structure",
                "composition",
                "silhouette",
                "controlnet",
                "same layout",
            )
        )

    def _finish(self, plan, provider, *, used_fallback, reason="", raw_text=None):
        print(f"[Planning Agent] Dynamic planner provider: {provider}")
        print(f"[Planning Agent] Planner fallback: {bool(used_fallback)}")
        return {
            "tool_plan": plan,
            "planning_mode": provider if not used_fallback else "rule",
            "llm_tool_planner_enabled": provider == "openai" and not used_fallback,
            "planner_used_fallback": bool(used_fallback),
            "planner_fallback_reason": reason,
            "tool_planner_raw_text": raw_text,
        }
