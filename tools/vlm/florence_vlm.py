from tools.vlm.base_vlm import BaseVLM


class FlorenceVLM(BaseVLM):
    def analyze(self, image, prompt: str | None = None) -> dict:
        print("[FlorenceVLM] Skeleton provider. Using fallback vision result.")
        caption = "An uploaded image"
        return {
            "caption": caption,
            "detailed_description": (
                "Florence-2 skeleton provider is not connected yet. "
                "Fallback vision description is used."
            ),
            "objects": [],
            "style_hints": [],
            "character_hints": {},
            "model": "florence2_skeleton",
            "used_fallback": True,
        }
