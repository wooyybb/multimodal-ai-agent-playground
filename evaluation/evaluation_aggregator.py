from evaluation.aesthetic_metric import AestheticMetric
from evaluation.clip_metric import ClipMetric
from evaluation.identity_metric import IdentityMetric
from evaluation.prompt_metric import PromptMetric


class EvaluationAggregator:
    WEIGHTS = {
        "clip": 0.55,
        "identity": 0.20,
        "prompt": 0.15,
        "aesthetic": 0.10,
    }

    def __init__(self, clip_tool=None, metrics=None):
        self.metrics = metrics or [
            ClipMetric(clip_tool=clip_tool),
            IdentityMetric(),
            PromptMetric(),
            AestheticMetric(),
        ]

    def evaluate(self, state: dict) -> dict:
        print("[EvaluationAggregator] Running...")
        metric_results = []
        for metric in self.metrics:
            result = metric.evaluate(state)
            metric_results.append(result)
            print(
                "[EvaluationAggregator] Metric: "
                f"{result['name']} Score: {result['score']:.4f}"
            )

        weighted_score = self._weighted_score(metric_results)
        summary = self._summary(metric_results, weighted_score)
        print(f"[EvaluationAggregator] Weighted: {weighted_score:.4f}")
        return {
            "metrics": metric_results,
            "weighted_score": weighted_score,
            "metric_summary": summary,
        }

    def _weighted_score(self, metric_results):
        total_weight = 0.0
        weighted = 0.0
        for result in metric_results:
            weight = self.WEIGHTS.get(result.get("name"), 0.0)
            total_weight += weight
            weighted += result.get("score", 0.0) * weight
        if total_weight <= 0:
            return 0.0
        return round(weighted / total_weight, 4)

    def _summary(self, metric_results, weighted_score):
        parts = [
            f"{item['name']}={item['score']:.2f}"
            for item in metric_results
        ]
        return f"weighted={weighted_score:.2f}; " + ", ".join(parts)
