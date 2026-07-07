from llm.requirement_parser import RequirementParser


class LLMStyleTransferPlanner:
    def __init__(self, requirement_parser=None):
        self.requirement_parser = requirement_parser or RequirementParser()

    def run(self, state: dict) -> dict:
        print("[LLMStyleTransferPlanner] Running Requirement Parser...")
        parsed = self.requirement_parser.parse(state or {})
        metadata = parsed.get("requirement_parser") or {}
        requirement_program = parsed.get("requirement_program") or {}
        final_program = parsed.get("final_style_transfer_program") or {}
        reasoning_summary = parsed.get("reasoning_summary", "")
        used_fallback = bool(parsed.get("parser_fallback"))

        print(f"[LLMStyleTransferPlanner] Parser provider: {parsed.get('parser_provider')}")
        print(f"[LLMStyleTransferPlanner] Parser fallback: {used_fallback}")
        return {
            "requirement_parser": metadata,
            "parser_provider": parsed.get("parser_provider"),
            "parser_fallback": used_fallback,
            "requirement_program": requirement_program,
            "llm_style_transfer_program": requirement_program,
            "llm_used_fallback": used_fallback,
            "llm_reasoning_summary": reasoning_summary,
            "llm_reasoning_raw_text": parsed.get("llm_reasoning_raw_text", ""),
            "final_style_transfer_program": final_program,
            "style_transfer_program": final_program,
            "generation_strategy": final_program.get("generation_strategy", {}),
            "llm_style_transfer_metadata": metadata,
        }
