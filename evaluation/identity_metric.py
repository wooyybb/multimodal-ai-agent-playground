from evaluation.metric_base import BaseMetric


class IdentityMetric(BaseMetric):
    name = "identity"

    def evaluate(self, state: dict) -> dict:
        prompt = str(
            state.get("provider_prompt")
            or state.get("final_prompt")
            or ""
        ).lower()
        character_program = state.get("character_program") or {}
        identity_terms = ("identity", "preserve", "recognizable", "character", "subject")
        accessory_terms = self._accessory_terms(character_program)

        score = 0.45
        if any(term in prompt for term in identity_terms):
            score += 0.25
        if character_program:
            score += 0.15
        if accessory_terms and any(term in prompt for term in accessory_terms):
            score += 0.15

        reason = "rule-based identity preservation check"
        if not character_program:
            reason += "; character_program unavailable"
        return self._result(score, reason)

    def _accessory_terms(self, character_program):
        appearance = character_program.get("appearance") or {}
        return [str(item).lower() for item in appearance.get("accessories", [])]
