import os

from tools.vlm.blip_vlm import BLIPVLM
from tools.vlm.florence_vlm import FlorenceVLM
class VLMRouter:
    def __init__(self, provider: str | None = None, blip_tool=None):
        self.provider = provider
        self.blip_tool = blip_tool

    def select(self):
        provider = (self.provider or os.getenv("VLM_PROVIDER") or "blip").lower()
        print(f"[VLMRouter] Provider: {provider}")

        if provider == "blip":
            return BLIPVLM(blip_tool=self.blip_tool)
        if provider == "florence":
            return FlorenceVLM(blip_tool=self.blip_tool)

        print("[VLMRouter] Unsupported provider. Falling back to BLIP")
        return BLIPVLM(blip_tool=self.blip_tool)
