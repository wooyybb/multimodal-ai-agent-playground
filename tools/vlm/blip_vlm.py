from tools.blip_tool import BlipTool
from tools.vlm.base_vlm import BaseVLM


class BLIPVLM(BaseVLM):
    def __init__(self, blip_tool=None):
        self.blip_tool = blip_tool or BlipTool()

    def analyze(self, image, prompt: str | None = None) -> dict:
        print("[BLIPVLM] Analyzing image...")
        caption = self.blip_tool.generate_caption(image)
        return {
            "caption": caption,
            "detailed_description": self._build_description(caption, prompt),
            "objects": [],
            "style_hints": [],
            "character_hints": {},
            "model": "blip",
            "used_fallback": False,
        }

    def _build_description(self, caption, prompt):
        if prompt:
            return f"{caption}. User visual intent: {prompt}"
        return caption
