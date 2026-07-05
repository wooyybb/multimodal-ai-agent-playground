import os

from tools.vlm.blip_vlm import BLIPVLM
from tools.vlm.florence_vlm import FlorenceVLM
from tools.vlm.qwen_vlm import QwenVLM


class VLMRouter:
    def __init__(self, provider: str | None = None, blip_tool=None):
        self.provider = provider
        self.blip_tool = blip_tool

    def select(self):
        provider = (self.provider or os.getenv("VLM_PROVIDER") or "blip").lower()
        print(f"[VLMRouter] Provider: {provider}")

        if provider == "blip":
            return BLIPVLM(blip_tool=self.blip_tool)
        if provider in ("florence", "florence2", "florence-2"):
            return FlorenceVLM(blip_tool=self.blip_tool)
        if provider in ("qwen", "qwen2.5-vl", "qwen-vl"):
            return QwenVLM(blip_tool=self.blip_tool)

        print("[VLMRouter] Falling back to BLIP")
        return BLIPVLM(blip_tool=self.blip_tool)
