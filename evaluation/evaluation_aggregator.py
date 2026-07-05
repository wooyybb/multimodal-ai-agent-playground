from evaluation.aesthetic_metric import AestheticMetric
from evaluation.clip_metric import ClipMetric
from evaluation.dino_metric import DINOIdentityMetric
from evaluation.identity_metric import IdentityMetric
from evaluation.prompt_metric import PromptMetric


class EvaluationAggregator:
    WEIGHTS = {
        "clip": 0.40,
        "dino_identity": 0.25,
        "prompt": 0.20,
        "aesthetic": 0.15,
    }
    FALLBACK_WEIGHTS = {
        "clip": 0.55,
        "identity": 0.20,
        "prompt": 0.15,
        "aesthetic": 0.10,
    }

    def __init__(self, clip_tool=None, metrics=None):
        self.metrics = (
            metrics
            if metrics is not None
            else [
                ClipMetric(clip_tool=clip_tool),
                DINOIdentityMetric(),
                IdentityMetric(),
                PromptMetric(),
                AestheticMetric(),
            ]
        )

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
        metric_results.extend(self._planned_metric_skeletons(metric_results))

        weighted_score = self._weighted_score(metric_results)
        categories = self._category_scores(metric_results, weighted_score)
        summary = self._summary(metric_results, weighted_score)
        print(f"[EvaluationAggregator] Weighted: {weighted_score:.4f}")
        return {
            "metrics": metric_results,
            "semantic_alignment": categories["semantic_alignment"],
            "identity_preservation": categories["identity_preservation"],
            "prompt_consistency": categories["prompt_consistency"],
            "aesthetic_quality": categories["aesthetic_quality"],
            "overall_score": weighted_score,
            "weighted_score": weighted_score,
            "metric_summary": summary,
            "metric_routing": self._metric_routing(state),
        }

    def _weighted_score(self, metric_results):
        weights = self._weights(metric_results)
        total_weight = 0.0
        weighted = 0.0
        for result in metric_results:
            weight = weights.get(result.get("name"), 0.0)
            total_weight += weight
            weighted += result.get("score", 0.0) * weight
        if total_weight <= 0:
            return 0.0
        return round(weighted / total_weight, 4)

    def _category_scores(self, metric_results, weighted_score):
        metric_map = {
            item.get("name"): item
            for item in metric_results
            if isinstance(item, dict)
        }
        dino = metric_map.get("dino_identity") or {}
        identity = metric_map.get("identity") or {}
        identity_score = (
            dino.get("score", 0.0)
            if dino.get("enabled")
            else identity.get("score", 0.0)
        )
        return {
            "semantic_alignment": (metric_map.get("clip") or {}).get("score", 0.0),
            "identity_preservation": identity_score,
            "prompt_consistency": (metric_map.get("prompt") or {}).get("score", 0.0),
            "aesthetic_quality": (metric_map.get("aesthetic") or {}).get("score", 0.0),
            "overall_score": weighted_score,
        }

    def _summary(self, metric_results, weighted_score):
        parts = [
            f"{item['name']}={item['score']:.2f}"
            for item in metric_results
        ]
        return f"weighted={weighted_score:.2f}; " + ", ".join(parts)

    def _planned_metric_skeletons(self, metric_results):
        existing = {
            item.get("name")
            for item in metric_results
            if isinstance(item, dict)
        }
        skeletons = []
        if "dino_identity" not in existing:
            skeletons.append(
                {
                    "name": "dino_identity",
                    "score": 0.0,
                    "enabled": False,
                    "reason": "DINO identity metric is planned but not enabled",
                    "used_fallback": True,
                }
            )
        skeletons.append(
            {
                "name": "vlm_judge",
                "score": 0.0,
                "enabled": False,
                "reason": "VLM judge is planned but not enabled",
            }
        )
        return skeletons

    def _weights(self, metric_results):
        dino = next(
            (
                item
                for item in metric_results
                if isinstance(item, dict) and item.get("name") == "dino_identity"
            ),
            {},
        )
        if dino.get("enabled"):
            return self.WEIGHTS
        return self.FALLBACK_WEIGHTS

    def _metric_routing(self, state):
        return {
            "clip": "clip_prompt"
            if state.get("clip_prompt")
            else "evaluation_prompt"
            if state.get("evaluation_prompt")
            else "provider_prompt"
            if state.get("provider_prompt")
            else "user_prompt",
            "prompt": "generation_prompt + context_program",
            "aesthetic": "pickscore_prompt"
            if state.get("pickscore_prompt")
            else "generation_prompt",
            "vlm_judge": "vlm_judge_prompt (skeleton disabled)",
            "dino_identity": "reference image -> generated image visual similarity",
        }
