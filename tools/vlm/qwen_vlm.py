from tools.vlm.base_vlm import BaseVLM
from tools.vlm.blip_vlm import BLIPVLM


class QwenVLM(BaseVLM):
    def __init__(self, blip_tool=None):
        self.fallback = BLIPVLM(
            blip_tool=blip_tool,
            provider="qwen",
            model="blip_fallback_for_qwen",
            used_fallback=True,
        )

    def analyze(self, image, prompt: str | None = None) -> dict:
        print("[QwenVLM] Skeleton provider. Falling back to BLIP.")
        result = self.fallback.analyze(image, prompt=prompt)
        result["detailed_description"] = (
            f"{result.get('detailed_description', '')} "
            "Qwen-VL skeleton provider is not connected yet."
        ).strip()
        return result
