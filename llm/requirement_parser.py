from context.style_transfer_program import StyleTransferProgramBuilder
from context.style_transfer_schema import StyleTransferSchema
from llm.openai_reasoner import dumps_payload
from llm.reasoner_router import ReasonerRouter


class RequirementParser:
    def __init__(self, reasoner_router=None):
        self.reasoner_router = reasoner_router or ReasonerRouter()
        self.schema = StyleTransferSchema()

    def parse(self, state: dict) -> dict:
        print("[RequirementParser] Running...")
        state = state or {}
        rule_program = (
            state.get("style_transfer_program")
            or StyleTransferProgramBuilder().build(state)
        )
        fallback_requirement = self.schema.from_rule_program_v4(rule_program)
        result = self.reasoner_router.reason(
            self._system_prompt(),
            dumps_payload(self._payload(state, rule_program)),
            fallback=fallback_requirement,
            schema_name="requirement_style_transfer_program",
        )
        requirement_program = self.schema.normalize_v4_requirement(
            result,
            fallback_requirement,
        )
        legacy_program = self.schema.v4_to_legacy_program(
            requirement_program,
            rule_program,
        )
        used_fallback = bool(result.get("reasoning_used_fallback"))
        metadata = {
            "parser": "requirement_parser",
            "parser_provider": result.get("reasoning_provider")
            or result.get("llm_provider"),
            "parser_fallback": used_fallback,
            "json_parse_success": result.get("llm_json_parse_success"),
            "latency": result.get("reasoning_latency"),
            "fallback_reason": result.get("reasoning_fallback_reason")
            or result.get("fallback_reason", ""),
        }
        reasoning_summary = self._reasoning_summary(requirement_program, metadata)
        print(f"[RequirementParser] Provider: {metadata.get('parser_provider')}")
        print(f"[RequirementParser] Fallback: {used_fallback}")
        return {
            "requirement_parser": metadata,
            "parser_provider": metadata.get("parser_provider"),
            "parser_fallback": used_fallback,
            "requirement_program": requirement_program,
            "style_transfer_program": legacy_program,
            "final_style_transfer_program": legacy_program,
            "reasoning_summary": reasoning_summary,
            "llm_reasoning_raw_text": result.get("llm_reasoning_raw_text", ""),
        }

    def _payload(self, state, rule_program):
        return {
            "user_long_prompt": state.get("user_prompt", ""),
            "vision_result": state.get("vision_result"),
            "reference_image_parser": state.get("reference_image"),
            "character_program": state.get("character_program"),
            "existing_style_transfer_program": rule_program,
        }

    def _system_prompt(self):
        return (
            "You are an LLM Requirement Parser for a reference-aware style "
            "transfer AI Agent. Do not write a final prompt. Return JSON only. "
            "Convert the user requirement into this JSON schema: task {type, goal}, "
            "identity {preserve_identity, preserve_outfit, preserve_hairstyle, "
            "preserve_palette}, style {renderer, anime_strength, lighting, palette, "
            "texture}, layout {camera, composition, panel_type, panel_count}, "
            "scene {background, decorations, mood}, pose {interaction, energy, "
            "naturalness}, text {enabled, style, language}, negative {remove}, "
            "generation_strategy {identity_strength, style_strength, "
            "composition_strength}. Use concise structured values."
        )

    def _reasoning_summary(self, program, metadata):
        task = program.get("task") or {}
        style = program.get("style") or {}
        return (
            f"Parsed requirement as {task.get('type', 'style transfer')} with "
            f"goal '{task.get('goal', '')}' and renderer "
            f"'{style.get('renderer', '')}'. Fallback={metadata.get('parser_fallback')}."
        )
