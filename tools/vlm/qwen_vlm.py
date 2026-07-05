from tools.vlm.base_vlm import BaseVLM
from tools.vlm.blip_vlm import BLIPVLM


class QwenVLM(BaseVLM):
    def __init__(self, blip_tool=None):
        self.fallback = BLIPVLM(
            blip_tool=blip_tool,
            provider="qwen2.5-vl",
            model="blip_fallback_for_qwen",
            used_fallback=True,
        )

    def analyze(self, image, prompt: str | None = None) -> dict:
        print("[QwenVLM] Skeleton provider. Falling back to BLIP.")
        result = self.fallback.analyze(image, prompt=prompt)
        detailed = (
            f"{result.get('detailed_caption') or result.get('detailed_description', '')} "
            "Qwen-VL skeleton provider is not connected yet."
        ).strip()
        result["provider"] = "qwen2.5-vl"
        result["detailed_caption"] = detailed
        result["detailed_description"] = detailed
        return result
