class BaseMetric:
    name = "base"

    def evaluate(self, state: dict) -> dict:
        raise NotImplementedError

    def _result(self, score, reason, enabled=True, used_fallback=False):
        return {
            "name": self.name,
            "score": self._clamp(score),
            "enabled": bool(enabled),
            "reason": reason,
            "used_fallback": bool(used_fallback),
        }

    def _clamp(self, score):
        try:
            value = float(score)
        except (TypeError, ValueError):
            value = 0.0
        return max(0.0, min(1.0, value))
