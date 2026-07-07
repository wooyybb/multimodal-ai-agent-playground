from context.style_transfer_schema import StyleTransferSchema
from context.style_transfer_program import StyleTransferProgramBuilder
from llm.openai_reasoner import dumps_payload
from llm.reasoner_router import ReasonerRouter


class LLMStyleTransferPlanner:
    def __init__(self, reasoner_router=None):
        self.reasoner_router = reasoner_router or ReasonerRouter()
        self.schema = StyleTransferSchema()

    def run(self, state: dict) -> dict:
        print("[LLMStyleTransferPlanner] Running...")
        state = state or {}
        rule_program = (
            state.get("style_transfer_program")
            or StyleTransferProgramBuilder().build(state)
        )
        fallback_llm_program = self.schema.from_rule_program(rule_program)
        result = self.reasoner_router.reason(
            self._system_prompt(),
            dumps_payload(self._payload(state, rule_program)),
            fallback=fallback_llm_program,
            schema_name="style_transfer_program",
        )
        llm_program = self.schema.normalize(result, rule_program)
        final_program = self.schema.to_legacy_program(llm_program, rule_program)
        used_fallback = bool(result.get("reasoning_used_fallback"))
        reasoning_summary = llm_program.get("reasoning_summary", "")
        print(f"[LLMStyleTransferPlanner] Used fallback: {used_fallback}")
        print(f"[LLMStyleTransferPlanner] Style goal: {llm_program.get('style_goal', '')}")
        return {
            "llm_style_transfer_program": llm_program,
            "llm_used_fallback": used_fallback,
            "llm_reasoning_summary": reasoning_summary,
            "llm_reasoning_raw_text": result.get("llm_reasoning_raw_text", ""),
            "final_style_transfer_program": final_program,
            "style_transfer_program": final_program,
            "generation_strategy": llm_program.get("generation_strategy", {}),
            "llm_style_transfer_metadata": {
                "provider": result.get("reasoning_provider") or result.get("llm_provider"),
                "latency": result.get("reasoning_latency"),
                "json_parse_success": result.get("llm_json_parse_success"),
                "fallback_reason": result.get("reasoning_fallback_reason")
                or result.get("fallback_reason", ""),
            },
        }

    def _payload(self, state, rule_program):
        return {
            "user_prompt": state.get("user_prompt"),
            "reference_image": state.get("reference_image"),
            "vision_result": state.get("vision_result"),
            "reference_image_parser_result": state.get("reference_image"),
            "character_program": state.get("character_program"),
            "existing_style_transfer_program": rule_program,
        }

    def _system_prompt(self):
        return (
            "You are an AI Agent planner for reference-aware style transfer. "
            "Return only JSON. Do not write a final image prompt. "
            "Create a structured Style Transfer Program with keys: task_type, "
            "style_goal, identity_policy, style, layout, generation_strategy, "
            "forbidden_concepts, negative_prompt, reasoning_summary. "
            "generation_strategy must include provider, use_img2img, "
            "use_ip_adapter, use_controlnet, style_strength, identity_strength, "
            "and structure_strength."
        )
