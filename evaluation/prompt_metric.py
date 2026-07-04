from evaluation.metric_base import BaseMetric


class PromptMetric(BaseMetric):
    name = "prompt"

    REQUIRED_HINTS = ("subject", "style", "layout", "lighting")

    def evaluate(self, state: dict) -> dict:
        package = state.get("compiled_prompt_package") or {}
        blocks = package.get("prompt_blocks") or {}
        prompt = str(
            package.get("positive_prompt")
            or state.get("provider_prompt")
            or state.get("final_prompt")
            or ""
        )

        if blocks:
            present = [key for key in self.REQUIRED_HINTS if blocks.get(key)]
            score = len(present) / len(self.REQUIRED_HINTS)
            reason = f"prompt blocks present: {present}"
        else:
            words = prompt.split()
            score = 0.75 if 8 <= len(words) <= 120 else 0.55
            reason = "prompt block data unavailable; used prompt length heuristic"

        return self._result(score, reason)
