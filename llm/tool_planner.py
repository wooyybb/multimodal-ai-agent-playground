from core.tool_plan_schema import ToolPlanSchema
from llm.openai_reasoner import dumps_payload
from llm.reasoner_router import ReasonerRouter


class ToolPlanner:
    def __init__(self, provider=None):
        self.router = ReasonerRouter(provider)

    def plan(self, payload, tool_catalog):
        fallback_plan = ToolPlanSchema.rule_plan(
            goal=str(payload.get("user_prompt") or "Reference-aware style transfer")
        )
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
