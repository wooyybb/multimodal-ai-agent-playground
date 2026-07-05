from evaluation.metric_base import BaseMetric
from tools.clip_tool import ClipTool


class ClipMetric(BaseMetric):
    name = "clip"

    def __init__(self, clip_tool=None):
        self.clip_tool = clip_tool or ClipTool()

    def evaluate(self, state: dict) -> dict:
        prompt, prompt_type = self._select_prompt(state)
        print(f"[CLIPMetric] Using prompt type: {prompt_type}")
        try:
            score = self.clip_tool.evaluate(
                state.get("reference_image"),
                state.get("generated_image_path"),
                prompt,
            )
            result = self._result(score, "CLIP image-text similarity")
        except Exception as error:
            result = self._result(
                0.0,
                f"CLIP metric unavailable: {error}",
                enabled=False,
                used_fallback=True,
            )
        result["prompt_type"] = prompt_type
        result["prompt"] = prompt
        return result

    def _select_prompt(self, state):
        for key in ("clip_prompt", "evaluation_prompt", "provider_prompt", "user_prompt"):
            prompt = state.get(key)
            if prompt:
                return str(prompt), key
        return "", "empty"
