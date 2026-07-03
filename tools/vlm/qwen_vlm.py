from tools.vlm.base_vlm import BaseVLM


class QwenVLM(BaseVLM):
    def analyze(self, image, prompt: str | None = None) -> dict:
        print("[QwenVLM] Skeleton provider. Using fallback vision result.")
        caption = "An uploaded image"
        return {
            "caption": caption,
            "detailed_description": (
                "Qwen-VL skeleton provider is not connected yet. "
                "Fallback vision description is used."
            ),
            "objects": [],
            "style_hints": [],
            "character_hints": {},
            "model": "qwen_vl_skeleton",
            "used_fallback": True,
        }
