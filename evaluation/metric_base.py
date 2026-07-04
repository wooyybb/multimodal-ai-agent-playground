class BaseMetric:
    name = "base"

    def evaluate(self, state: dict) -> dict:
        raise NotImplementedError

    def _result(self, score, reason):
        return {
            "name": self.name,
            "score": self._clamp(score),
            "reason": reason,
        }

    def _clamp(self, score):
        try:
            value = float(score)
        except (TypeError, ValueError):
            value = 0.0
        return max(0.0, min(1.0, value))
