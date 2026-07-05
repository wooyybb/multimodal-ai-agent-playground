from evaluation.metric_base import BaseMetric


class PromptMetric(BaseMetric):
    name = "prompt"

    REQUIRED_HINTS = ("subject", "style", "layout", "lighting")

    def evaluate(self, state: dict) -> dict:
        package = state.get("compiled_prompt_package") or {}
        blocks = package.get("prompt_blocks") or {}
        context_program = state.get("context_program") or {}
        prompt = str(
            state.get("generation_prompt")
            or package.get("positive_prompt")
            or state.get("provider_prompt")
            or state.get("final_prompt")
            or ""
        ).lower()
        negative_prompt = str(
            state.get("provider_negative_prompt")
            or state.get("negative_prompt")
            or (package.get("negative_prompt") if isinstance(package, dict) else "")
            or ""
        )

        if blocks:
            present = [key for key in self.REQUIRED_HINTS if blocks.get(key)]
            context_checks = self._context_checks(prompt, context_program)
            negative_separated = bool(negative_prompt)
            score = (
                len(present) / len(self.REQUIRED_HINTS) * 0.55
                + sum(context_checks.values()) / len(context_checks) * 0.35
                + (0.10 if negative_separated else 0.0)
            )
            reason = (
                f"prompt blocks present: {present}; "
                f"context checks: {context_checks}; "
                f"negative separated: {negative_separated}"
            )
        else:
            words = prompt.split()
            score = 0.75 if 8 <= len(words) <= 120 else 0.55
            reason = "prompt block data unavailable; used prompt length heuristic"

        result = self._result(score, reason)
        result["prompt_type"] = "generation_prompt"
        return result

    def _context_checks(self, prompt, context_program):
        characters = context_program.get("characters") or {}
        style = context_program.get("style") or {}
        layout = context_program.get("layout") or {}
        lighting = context_program.get("lighting") or {}
        return {
            "character": self._section_present(prompt, characters, ("character", "subject", "identity")),
            "style": self._section_present(prompt, style, ("style", "anime", "rendering")),
            "layout": self._section_present(prompt, layout, ("layout", "composition", "camera", "portrait")),
            "lighting": self._section_present(prompt, lighting, ("lighting", "light", "shadow", "mood")),
        }

    def _section_present(self, prompt, section, fallback_terms):
        if not section:
            return False
        section_text = self._flatten(section).lower()
        if any(term in prompt for term in fallback_terms):
            return True
        return any(token and token in prompt for token in section_text.split()[:12])

    def _flatten(self, value):
        if isinstance(value, dict):
            return " ".join(self._flatten(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(self._flatten(item) for item in value)
        return str(value or "")
