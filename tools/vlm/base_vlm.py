from abc import ABC, abstractmethod


class BaseVLM(ABC):
    @abstractmethod
    def analyze(self, image, prompt: str | None = None) -> dict:
        """Return structured vision understanding for an input image."""

    def standard_result(
        self,
        *,
        caption: str = "",
        detailed_caption: str = "",
        detailed_description: str = "",
        objects: list | None = None,
        characters: list | None = None,
        scene: dict | None = None,
        style: dict | None = None,
        colors: dict | None = None,
        composition: dict | None = None,
        character_hints: dict | None = None,
        style_hints: list | None = None,
        composition_hints: dict | None = None,
        color_hints: dict | None = None,
        model: str = "",
        provider: str = "",
        used_fallback: bool = False,
        latency: float = 0.0,
    ) -> dict:
        character_hints = character_hints or {}
        composition_hints = composition_hints or {}
        color_hints = color_hints or {}
        objects = objects or []
        detailed = detailed_caption or detailed_description or caption or ""
        characters = characters or self._characters_from_hints(character_hints)
        colors = colors or {
            "dominant": color_hints.get("dominant", []) or [],
            "accent": color_hints.get("accent", []) or [],
        }
        composition = composition or {
            "camera": composition_hints.get("camera", ""),
            "framing": composition_hints.get("framing", ""),
            "viewpoint": composition_hints.get("viewpoint", ""),
        }
        style = style or {
            "keywords": style_hints or [],
            "rendering": ", ".join(style_hints or []),
        }
        scene = scene or {
            "summary": detailed,
            "objects": objects,
        }
        return {
            "caption": caption or "",
            "detailed_caption": detailed,
            "objects": objects,
            "characters": characters,
            "scene": scene,
            "style": style,
            "colors": colors,
            "composition": composition,
            "provider": provider or "unknown",
            "used_fallback": bool(used_fallback),
            "latency": float(latency or 0.0),
            # Backward-compatible aliases used by older agents/debug views.
            "detailed_description": detailed,
            "character_hints": {
                "gender": character_hints.get("gender", ""),
                "outfit": character_hints.get("outfit", ""),
                "hair": character_hints.get("hair", ""),
                "accessories": character_hints.get("accessories", []) or [],
                "pose": character_hints.get("pose", ""),
                "expression": character_hints.get("expression", ""),
            },
            "style_hints": style_hints or [],
            "composition_hints": composition,
            "color_hints": colors,
            "model": model or provider or "unknown_vlm",
        }

    def _characters_from_hints(self, character_hints):
        if not any(character_hints.values()):
            return []
        return [
            {
                "gender": character_hints.get("gender", ""),
                "outfit": character_hints.get("outfit", ""),
                "hair": character_hints.get("hair", ""),
                "accessories": character_hints.get("accessories", []) or [],
                "pose": character_hints.get("pose", ""),
                "expression": character_hints.get("expression", ""),
            }
        ]
