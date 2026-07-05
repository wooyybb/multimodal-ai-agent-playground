from tools.blip_tool import BlipTool
from tools.vlm.base_vlm import BaseVLM
from time import perf_counter


class BLIPVLM(BaseVLM):
    COLOR_WORDS = (
        "white",
        "black",
        "red",
        "blue",
        "green",
        "gold",
        "silver",
        "pink",
        "brown",
        "blonde",
        "purple",
        "gray",
    )

    ACCESSORY_WORDS = (
        "sword",
        "hat",
        "glasses",
        "bag",
        "armor",
        "ribbon",
        "necklace",
        "earrings",
        "weapon",
    )

    def __init__(
        self,
        blip_tool=None,
        provider: str = "blip",
        model: str = "blip",
        used_fallback: bool = False,
    ):
        self.blip_tool = blip_tool or BlipTool()
        self.provider = provider
        self.model = model
        self.used_fallback = used_fallback

    def analyze(self, image, prompt: str | None = None) -> dict:
        print("[BLIPVLM] Analyzing image...")
        started = perf_counter()
        caption = self.blip_tool.generate_caption(image)
        text = " ".join([caption or "", prompt or ""]).lower()
        character_hints = self._character_hints(text)
        style_hints = self._style_hints(text)
        composition_hints = self._composition_hints(text)
        color_hints = self._color_hints(text)
        objects = self._objects(text)
        return self.standard_result(
            caption=caption,
            detailed_caption=self._build_description(caption, prompt),
            objects=objects,
            character_hints=character_hints,
            style_hints=style_hints,
            composition_hints=composition_hints,
            color_hints=color_hints,
            scene={"summary": caption, "objects": objects},
            style={"keywords": style_hints, "rendering": ", ".join(style_hints)},
            colors=color_hints,
            composition=composition_hints,
            model=self.model,
            provider=self.provider,
            used_fallback=self.used_fallback,
            latency=round(perf_counter() - started, 4),
        )

    def _build_description(self, caption, prompt):
        if prompt:
            return f"{caption}. User visual intent: {prompt}"
        return caption

    def _character_hints(self, text):
        gender = ""
        if any(word in text for word in ("woman", "girl", "female", "lady")):
            gender = "female"
        elif any(word in text for word in ("man", "boy", "male", "gentleman")):
            gender = "male"

        return {
            "gender": gender,
            "outfit": self._outfit(text),
            "hair": self._hair(text),
            "accessories": [word for word in self.ACCESSORY_WORDS if word in text],
            "pose": self._pose(text),
            "expression": self._expression(text),
        }

    def _style_hints(self, text):
        hints = []
        if "anime" in text:
            hints.append("anime")
        if "webtoon" in text:
            hints.append("soft webtoon")
        if "line art" in text:
            hints.append("clean line art")
        if "realistic" in text or "photo" in text:
            hints.append("realistic")
        return hints

    def _composition_hints(self, text):
        camera = ""
        if "close up" in text or "close-up" in text:
            camera = "close_up"
        elif "full body" in text:
            camera = "full_body"
        elif "portrait" in text:
            camera = "medium"

        framing = ""
        if "photobooth" in text:
            framing = "photobooth strip"
        elif "poster" in text:
            framing = "poster"
        elif "portrait" in text:
            framing = "portrait"

        viewpoint = "front" if any(word in text for word in ("standing", "portrait", "girl", "woman", "man")) else ""
        return {
            "camera": camera,
            "framing": framing,
            "viewpoint": viewpoint,
        }

    def _color_hints(self, text):
        dominant = [color for color in self.COLOR_WORDS if color in text]
        accent = [
            color
            for color in dominant
            if color in ("gold", "silver", "red", "blue", "pink", "purple")
        ]
        return {
            "dominant": dominant[:4],
            "accent": accent[:3],
        }

    def _objects(self, text):
        return [word for word in self.ACCESSORY_WORDS if word in text]

    def _hair(self, text):
        if "long hair" in text:
            return "long hair"
        if "short hair" in text:
            return "short hair"
        return ""

    def _pose(self, text):
        if "holding" in text and "sword" in text:
            return "holding a sword"
        if "standing" in text:
            return "standing"
        if "sitting" in text:
            return "sitting"
        if "portrait" in text:
            return "portrait pose"
        return ""

    def _expression(self, text):
        if "smile" in text or "smiling" in text:
            return "smiling"
        if "serious" in text:
            return "serious"
        if "sad" in text:
            return "sad"
        return ""

    def _outfit(self, text):
        for color in self.COLOR_WORDS:
            for noun in ("clothes", "robe", "dress", "shirt", "armor", "outfit"):
                phrase = f"{color} {noun}"
                if phrase in text:
                    return phrase
        for noun in ("robe", "dress", "armor", "uniform", "outfit"):
            if noun in text:
                return noun
        return ""
