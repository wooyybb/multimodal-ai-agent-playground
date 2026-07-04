from evaluation.evaluation_aggregator import EvaluationAggregator
from tools.clip_tool import ClipTool


class EvaluationScore(float):
    def __new__(cls, score, evaluation_result=None):
        obj = float.__new__(cls, score)
        obj.evaluation_result = evaluation_result or {}
        return obj

    def get(self, key, default=None):
        return self.evaluation_result.get(key, default)


class EvaluationAgent:
    def __init__(self, clip_tool=None):
        self.clip_tool = clip_tool or ClipTool()
        self.aggregator = EvaluationAggregator(clip_tool=self.clip_tool)

    def run(self, reference_image, generated_image_path, final_prompt) -> float:
        print("[EvaluationAgent] Running...")
        evaluation_result = self.aggregator.evaluate(
            {
                "reference_image": reference_image,
                "generated_image_path": generated_image_path,
                "final_prompt": final_prompt,
                "provider_prompt": final_prompt,
            }
        )
        score = evaluation_result.get("weighted_score", 0.0)
        print(f"[EvaluationAgent] Score: {score}")
        return EvaluationScore(score, evaluation_result)
