from evaluation.aesthetic_metric import AestheticMetric
from evaluation.clip_metric import ClipMetric
from evaluation.dino_metric import DINOIdentityMetric
from evaluation.evaluation_aggregator import EvaluationAggregator
from evaluation.prompt_metric import PromptMetric

CLIPMetric = ClipMetric

__all__ = [
    "AestheticMetric",
    "CLIPMetric",
    "ClipMetric",
    "DINOIdentityMetric",
    "EvaluationAggregator",
    "PromptMetric",
]
