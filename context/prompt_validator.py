from context.prompt_sanitizer import PromptSanitizer


class PromptValidator:
    def __init__(self):
        self.sanitizer = PromptSanitizer()

    def validate(
        self,
        prompts: dict,
        style_transfer_program: dict | None = None,
        forbidden_concepts=None,
    ) -> dict:
        prompts = prompts or {}
        style_transfer_program = style_transfer_program or {}
        forbidden_concepts = list(
            forbidden_concepts
            or style_transfer_program.get("forbidden_concepts")
            or []
        )
        sdxl_prompt = prompts.get("sdxl_style_prompt") or prompts.get("generation_prompt") or ""
        clip_prompt = prompts.get("clip_prompt") or ""
        survived = self._survived_forbidden(prompts, forbidden_concepts)
        duplicate_count = self._duplicate_count(prompts.get("generation_prompt") or "")
        sdxl_tokens = self.sanitizer.count_tokens(sdxl_prompt)
        clip_tokens = self.sanitizer.count_tokens(clip_prompt)
        required = self._required_preserved(prompts, style_transfer_program)
        warnings = []
        if survived:
            warnings.append("forbidden concepts survived prompt sanitization")
        if duplicate_count:
            warnings.append("duplicate phrases remain")
        if sdxl_tokens > 77:
            warnings.append("SDXL prompt exceeds 77 token limit")
        if clip_tokens > 77:
            warnings.append("CLIP prompt exceeds 77 token limit")
        if not required["style_preserved"]:
            warnings.append("style intent may be missing")
        if not required["layout_preserved"]:
            warnings.append("layout intent may be missing")

        return {
            "valid": not warnings,
            "forbidden_survived": survived,
            "duplicate_count": duplicate_count,
            "sdxl_token_count": sdxl_tokens,
            "clip_token_count": clip_tokens,
            "required_style_preserved": required["style_preserved"],
            "required_layout_preserved": required["layout_preserved"],
            "warnings": warnings,
        }

    def _survived_forbidden(self, prompts, forbidden_concepts):
        survived = []
        prompt_keys = (
            "generation_prompt",
            "sdxl_style_prompt",
            "clip_prompt",
            "pickscore_prompt",
            "vlm_judge_prompt",
        )
        searchable = " ".join(
            str(prompts.get(key) or "") for key in prompt_keys
        ).lower()
        for concept in forbidden_concepts:
            term = str(concept or "").lower()
            if term and term in searchable:
                survived.append(concept)
        return survived

    def _duplicate_count(self, prompt):
        phrases = [
            phrase.strip(" ,.").lower()
            for phrase in str(prompt or "").split(",")
            if phrase.strip()
        ]
        return len(phrases) - len(set(phrases))

    def _required_preserved(self, prompts, program):
        text = " ".join(str(value or "").lower() for value in prompts.values())
        style = program.get("style") or {}
        layout = program.get("layout") or {}
        style_terms = [
            style.get("name"),
            style.get("rendering"),
            style.get("mood"),
            style.get("texture"),
        ]
        style_terms += style.get("color_palette") or []
        layout_terms = [
            layout.get("format"),
            layout.get("structure"),
            layout.get("background"),
        ]
        layout_terms += layout.get("decorations") or []
        return {
            "style_preserved": self._any_term(text, style_terms),
            "layout_preserved": self._any_term(text, layout_terms),
        }

    def _any_term(self, text, terms):
        terms = [str(term).lower() for term in terms if str(term or "").strip()]
        if not terms:
            return True
        return any(term in text for term in terms)
