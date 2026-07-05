from evaluation.metric_base import BaseMetric


class AestheticMetric(BaseMetric):
    name = "aesthetic"

    def evaluate(self, state: dict) -> dict:
        prompt = str(
            state.get("pickscore_prompt")
            or state.get("generation_prompt")
            or state.get("provider_prompt")
            or state.get("final_prompt")
            or ""
        )
        negative = str(state.get("provider_negative_prompt") or state.get("negative_prompt") or "")
        words = prompt.split()

        score = 0.55
        if 12 <= len(words) <= 110:
            score += 0.2
        if any(term in prompt.lower() for term in ("high quality", "detailed", "lighting", "composition")):
            score += 0.15
        if negative:
            score += 0.1

        result = self._result(score, "rule-based aesthetic prompt structure check")
        result["prompt_type"] = "pickscore_prompt" if state.get("pickscore_prompt") else "generation_prompt"
        return result
