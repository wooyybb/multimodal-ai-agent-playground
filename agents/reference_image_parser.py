class ReferenceImageParser:
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
        "robe",
        "armor",
        "ribbon",
        "necklace",
        "earrings",
        "weapon",
    )

    def run(self, state: dict) -> dict:
        print("[ReferenceImageParser] Running...")
        state = state or {}
        vision_result = state.get("vision_result") or self._vision_result_from_caption(
            state.get("caption")
        )
        caption = str(state.get("caption") or vision_result.get("caption") or "")
        user_prompt = str(state.get("user_prompt") or "")
        scene_plan = state.get("scene_plan") or {}
        text = " ".join(
            [
                caption,
                str(vision_result.get("detailed_description") or ""),
                " ".join(vision_result.get("objects") or []),
                " ".join(vision_result.get("style_hints") or []),
                user_prompt,
            ]
        ).lower()

        reference_image = {
            "identity": self._identity(text, scene_plan),
            "appearance": self._appearance(text),
            "style": self._style(text),
            "composition": self._composition(text, scene_plan),
            "colors": self._colors(text),
            "identity_rules": self._identity_rules(text),
        }

        print(f"[ReferenceImageParser] Identity: {reference_image['identity']}")
        print(f"[ReferenceImageParser] Style: {reference_image['style']}")
        print(f"[ReferenceImageParser] Composition: {reference_image['composition']}")
        return {"reference_image": reference_image}

    def _vision_result_from_caption(self, caption):
        return getattr(caption, "vision_result", {}) or {}

    def _identity(self, text, scene_plan):
        gender = ""
        if any(word in text for word in ("woman", "girl", "female", "lady")):
            gender = "female"
        elif any(word in text for word in ("man", "boy", "male", "gentleman")):
            gender = "male"

        estimated_age = ""
        if any(word in text for word in ("girl", "boy", "child", "kid")):
            estimated_age = "young"
        elif any(word in text for word in ("woman", "man", "adult")):
            estimated_age = "adult"
        elif any(word in text for word in ("elderly", "old", "senior")):
            estimated_age = "senior"

        species = "human"
        if any(word in text for word in ("cat", "dog", "animal", "creature")):
            species = "non-human"

        role = scene_plan.get("scene_type") or ""
        if "sword" in text or "armor" in text:
            role = "warrior"
        elif "school" in text or "student" in text:
            role = "student"
        elif "princess" in text:
            role = "princess"

        return {
            "gender": gender,
            "estimated_age": estimated_age,
            "species": species,
            "role": role,
        }

    def _appearance(self, text):
        return {
            "hair": self._hair(text),
            "hair_color": self._first_color_before(text, "hair"),
            "eye_color": self._first_color_before(text, "eyes"),
            "skin": self._skin(text),
            "outfit": self._outfit(text),
            "accessories": [word for word in self.ACCESSORY_WORDS if word in text],
        }

    def _style(self, text):
        anime = 0.92 if "anime" in text else 0.72 if "webtoon" in text else 0.35
        realism = 0.86 if "realistic" in text or "photo" in text else 0.11 if anime > 0.7 else 0.45
        lineart = 0.87 if "line art" in text or "webtoon" in text or "anime" in text else 0.3
        rendering = ""
        if "webtoon" in text:
            rendering = "soft webtoon"
        elif "line art" in text:
            rendering = "clean line art"
        elif anime > 0.7:
            rendering = "anime illustration"
        elif realism > 0.8:
            rendering = "realistic rendering"
        return {
            "anime": anime,
            "realism": realism,
            "lineart": lineart,
            "rendering": rendering,
        }

    def _composition(self, text, scene_plan):
        camera = scene_plan.get("camera_view") or ""
        if "close up" in text or "close-up" in text:
            camera = "close_up"
        elif "full body" in text:
            camera = "full_body"
        elif "portrait" in text:
            camera = "medium"
        elif not camera:
            camera = "eye_level"

        framing = scene_plan.get("layout_type") or ""
        if "photobooth" in text:
            framing = "photobooth strip"
        elif "poster" in text:
            framing = "poster"
        elif "portrait" in text:
            framing = "portrait"
        elif not framing:
            framing = "single subject"

        viewpoint = "front"
        if "side view" in text:
            viewpoint = "side"
        elif "above" in text:
            viewpoint = "slightly_above"

        return {
            "camera": camera,
            "framing": framing,
            "viewpoint": viewpoint,
        }

    def _colors(self, text):
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

    def _identity_rules(self, text):
        rules = ["preserve reference image identity"]
        if "caption" in text:
            rules.append("stay faithful to source caption")
        if "sword" in text:
            rules.append("preserve sword as a key identity accessory")
        if "white" in text:
            rules.append("preserve white visual identity cues")
        if "anime" in text or "webtoon" in text:
            rules.append("preserve stylized illustration cues")
        return rules

    def _hair(self, text):
        if "long hair" in text:
            return "long hair"
        if "short hair" in text:
            return "short hair"
        return ""

    def _skin(self, text):
        if "pale skin" in text:
            return "pale skin"
        if "dark skin" in text:
            return "dark skin"
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

    def _first_color_before(self, text, noun):
        for color in self.COLOR_WORDS:
            if f"{color} {noun}" in text:
                return color
        return ""
