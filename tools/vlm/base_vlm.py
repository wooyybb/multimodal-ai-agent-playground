from abc import ABC, abstractmethod


class BaseVLM(ABC):
    @abstractmethod
    def analyze(self, image, prompt: str | None = None) -> dict:
        """Return structured vision understanding for an input image."""

    def standard_result(
        self,
        *,
        caption: str = "",
        detailed_description: str = "",
        objects: list | None = None,
        character_hints: dict | None = None,
        style_hints: list | None = None,
        composition_hints: dict | None = None,
        color_hints: dict | None = None,
        model: str = "",
        provider: str = "",
        used_fallback: bool = False,
    ) -> dict:
        character_hints = character_hints or {}
        composition_hints = composition_hints or {}
        color_hints = color_hints or {}
        return {
            "caption": caption or "",
            "detailed_description": detailed_description or caption or "",
            "objects": objects or [],
            "character_hints": {
                "gender": character_hints.get("gender", ""),
                "outfit": character_hints.get("outfit", ""),
                "hair": character_hints.get("hair", ""),
                "accessories": character_hints.get("accessories", []) or [],
                "pose": character_hints.get("pose", ""),
                "expression": character_hints.get("expression", ""),
            },
            "style_hints": style_hints or [],
            "composition_hints": {
                "camera": composition_hints.get("camera", ""),
                "framing": composition_hints.get("framing", ""),
                "viewpoint": composition_hints.get("viewpoint", ""),
            },
            "color_hints": {
                "dominant": color_hints.get("dominant", []) or [],
                "accent": color_hints.get("accent", []) or [],
            },
            "model": model or provider or "unknown_vlm",
            "provider": provider or "unknown",
            "used_fallback": bool(used_fallback),
        }
