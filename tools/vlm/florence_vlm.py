from tools.vlm.base_vlm import BaseVLM
from tools.vlm.blip_vlm import BLIPVLM


class FlorenceVLM(BaseVLM):
    def __init__(self, blip_tool=None):
        self.fallback = BLIPVLM(
            blip_tool=blip_tool,
            provider="florence",
            model="blip_fallback_for_florence",
            used_fallback=True,
        )

    def analyze(self, image, prompt: str | None = None) -> dict:
        print("[FlorenceVLM] Skeleton provider. Falling back to BLIP.")
        result = self.fallback.analyze(image, prompt=prompt)
        result["detailed_description"] = (
            f"{result.get('detailed_description', '')} "
            "Florence-2 skeleton provider is not connected yet."
        ).strip()
        return result
