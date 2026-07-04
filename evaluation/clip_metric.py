from evaluation.metric_base import BaseMetric
from tools.clip_tool import ClipTool


class ClipMetric(BaseMetric):
    name = "clip"

    def __init__(self, clip_tool=None):
        self.clip_tool = clip_tool or ClipTool()

    def evaluate(self, state: dict) -> dict:
        score = self.clip_tool.evaluate(
            state.get("reference_image"),
            state.get("generated_image_path"),
            state.get("final_prompt", ""),
        )
        return self._result(score, "CLIP image-text similarity")
