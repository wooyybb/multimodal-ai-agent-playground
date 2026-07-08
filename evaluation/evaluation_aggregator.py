from evaluation.metrics import (
    AestheticMetric,
    ClipMetric,
    DINOIdentityMetric,
    IdentityMetric,
    PromptMetric,
)


class EvaluationAggregator:
    RESULT_DEFAULTS = {
        "metrics": [],
        "semantic_alignment": 0.0,
        "identity_preservation": 0.0,
        "prompt_consistency": 0.0,
        "aesthetic_quality": 0.0,
        "overall_score": 0.0,
        "weighted_score": 0.0,
        "metric_summary": "",
        "used_fallback": False,
    }
    METRIC_DEFAULTS = {
        "name": "",
        "score": 0.0,
        "enabled": True,
        "reason": "",
        "used_fallback": False,
    }
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
        print("[Evaluation Layer] Running metrics...")
        metric_results = []
        for metric in self.metrics:
            try:
                result = metric.evaluate(state)
            except Exception as error:
                result = {
                    "name": getattr(metric, "name", metric.__class__.__name__),
                    "score": 0.0,
                    "enabled": False,
                    "reason": f"metric failed: {error}",
                    "used_fallback": True,
                }
            result = self._normalize_metric_result(result)
            metric_results.append(result)
            print(self._metric_log_line(result))
        metric_results.extend(
            self._normalize_metric_result(result)
            for result in self._planned_metric_skeletons(metric_results)
        )

        weighted_score = self._weighted_score(metric_results)
        categories = self._category_scores(metric_results, weighted_score)
        summary = self._summary(metric_results, weighted_score)
        used_fallback = self._used_fallback(metric_results, weighted_score)
        print(f"[Evaluation Layer] weighted_score={weighted_score:.4f}")
        result = {
            "metrics": metric_results,
            "semantic_alignment": categories["semantic_alignment"],
            "identity_preservation": categories["identity_preservation"],
            "prompt_consistency": categories["prompt_consistency"],
            "aesthetic_quality": categories["aesthetic_quality"],
            "overall_score": weighted_score,
            "weighted_score": weighted_score,
            "metric_summary": summary,
            "used_fallback": used_fallback,
            "metric_routing": self._metric_routing(state),
        }
        return self._normalize_evaluation_result(result)

    def _weighted_score(self, metric_results):
        weights = self._weights(metric_results)
        total_weight = 0.0
        weighted = 0.0
        for result in metric_results:
            if not result.get("enabled", True):
                continue
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
            if identity.get("enabled", True)
            else 0.0
        )
        return {
            "semantic_alignment": self._enabled_score(metric_map.get("clip")),
            "identity_preservation": identity_score,
            "prompt_consistency": self._enabled_score(metric_map.get("prompt")),
            "aesthetic_quality": self._enabled_score(metric_map.get("aesthetic")),
            "overall_score": weighted_score,
        }

    def _summary(self, metric_results, weighted_score):
        parts = [
            f"{item['name']}={item['score']:.2f}"
            + ("" if item.get("enabled", True) else " disabled")
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
                "used_fallback": True,
            }
        )
        return skeletons

    def _weights(self, metric_results):
        return self.WEIGHTS

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

    def _normalize_metric_result(self, result):
        normalized = dict(self.METRIC_DEFAULTS)
        if isinstance(result, dict):
            normalized.update(result)
        normalized["name"] = str(normalized.get("name") or "")
        normalized["score"] = self._clamp(normalized.get("score"))
        normalized["enabled"] = bool(normalized.get("enabled"))
        if not normalized["enabled"]:
            normalized["score"] = 0.0
        normalized["reason"] = str(normalized.get("reason") or "")
        normalized["used_fallback"] = bool(normalized.get("used_fallback"))
        return normalized

    def _normalize_evaluation_result(self, result):
        normalized = dict(self.RESULT_DEFAULTS)
        normalized.update(result or {})
        normalized["metrics"] = [
            self._normalize_metric_result(metric)
            for metric in normalized.get("metrics", [])
        ]
        for key in (
            "semantic_alignment",
            "identity_preservation",
            "prompt_consistency",
            "aesthetic_quality",
            "overall_score",
            "weighted_score",
        ):
            normalized[key] = self._clamp(normalized.get(key))
        normalized["metric_summary"] = str(normalized.get("metric_summary") or "")
        normalized["used_fallback"] = bool(normalized.get("used_fallback"))
        return normalized

    def _metric_log_line(self, result):
        if result.get("enabled", True):
            return f"[Evaluation Layer] {result['name']}: score={result['score']:.4f}"
        return (
            f"[Evaluation Layer] {result['name']}: "
            f"enabled=False reason={result.get('reason', '')}"
        )

    def _enabled_score(self, result):
        if not result or not result.get("enabled", True):
            return 0.0
        return self._clamp(result.get("score"))

    def _used_fallback(self, metric_results, weighted_score):
        enabled = [
            result
            for result in metric_results
            if result.get("enabled") and self.WEIGHTS.get(result.get("name"), 0.0) > 0
        ]
        if not enabled and weighted_score == 0.0:
            return True
        return any(result.get("used_fallback") for result in metric_results)

    def _clamp(self, score):
        try:
            value = float(score)
        except (TypeError, ValueError):
            value = 0.0
        return round(max(0.0, min(1.0, value)), 4)
