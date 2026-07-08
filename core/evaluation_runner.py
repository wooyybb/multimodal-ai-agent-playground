from evaluation.metrics import (
    AestheticMetric,
    ClipMetric,
    DINOIdentityMetric,
    PromptMetric,
)
from evaluation.evaluation_aggregator import EvaluationAggregator

CLIPMetric = ClipMetric

__all__ = [
    "AestheticMetric",
    "CLIPMetric",
    "ClipMetric",
    "DINOIdentityMetric",
    "EvaluationAggregator",
    "PromptMetric",
]
