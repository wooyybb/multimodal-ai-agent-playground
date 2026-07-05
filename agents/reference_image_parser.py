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
        structured = self._has_structured_fields(vision_result)
        characters = vision_result.get("characters") or []
        objects = vision_result.get("objects") or []
        style = vision_result.get("style") or {}
        colors = vision_result.get("colors") or {}
        composition = vision_result.get("composition") or {}
        character_hints = vision_result.get("character_hints") or {}
        composition_hints = vision_result.get("composition_hints") or {}
        color_hints = vision_result.get("color_hints") or {}
        caption = str(state.get("caption") or vision_result.get("caption") or "")
        user_prompt = str(state.get("user_prompt") or "")
        scene_plan = state.get("scene_plan") or {}
        text = self._vision_text(
            vision_result,
            caption,
            user_prompt,
            structured=structured,
        )

        reference_image = {
            "identity": self._identity(text, scene_plan, character_hints, characters),
            "appearance": self._appearance(text, character_hints, characters, objects),
            "style": self._style(text, style),
            "composition": self._composition(
                text,
                scene_plan,
                composition_hints,
                composition,
            ),
            "colors": self._colors(text, color_hints, colors),
            "identity_rules": self._identity_rules(text),
        }

        print(f"[ReferenceImageParser] Identity: {reference_image['identity']}")
        print(f"[ReferenceImageParser] Style: {reference_image['style']}")
        print(f"[ReferenceImageParser] Composition: {reference_image['composition']}")
        return {"reference_image": reference_image}

    def _vision_result_from_caption(self, caption):
        return getattr(caption, "vision_result", {}) or {}

    def _has_structured_fields(self, vision_result):
        return any(
            bool(vision_result.get(key))
            for key in ("characters", "objects", "colors", "composition")
        )

    def _vision_text(self, vision_result, caption, user_prompt, structured):
        if structured:
            return " ".join(
                [
                    self._stringify(vision_result.get("characters") or []),
                    self._stringify(vision_result.get("objects") or []),
                    self._stringify(vision_result.get("colors") or {}),
                    self._stringify(vision_result.get("composition") or {}),
                    self._stringify(vision_result.get("style") or {}),
                    user_prompt,
                ]
            ).lower()
        return " ".join(
            [
                caption,
                str(
                    vision_result.get("detailed_caption")
                    or vision_result.get("detailed_description")
                    or ""
                ),
                " ".join(vision_result.get("objects") or []),
                " ".join(vision_result.get("style_hints") or []),
                user_prompt,
            ]
        ).lower()

    def _identity(self, text, scene_plan, character_hints, characters):
        first_character = characters[0] if characters and isinstance(characters[0], dict) else {}
        gender = first_character.get("gender") or character_hints.get("gender", "")
        if any(word in text for word in ("woman", "girl", "female", "lady")):
            gender = gender or "female"
        elif any(word in text for word in ("man", "boy", "male", "gentleman")):
            gender = gender or "male"

        estimated_age = ""
        if self._contains_word(text, ("girl", "boy", "child", "kid")):
            estimated_age = "young"
        elif self._contains_word(text, ("woman", "man", "adult")):
            estimated_age = "adult"
        elif self._contains_word(text, ("elderly", "old", "senior")):
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

    def _appearance(self, text, character_hints, characters, objects):
        first_character = characters[0] if characters and isinstance(characters[0], dict) else {}
        hint_accessories = character_hints.get("accessories") or []
        character_accessories = first_character.get("accessories") or []
        parsed_accessories = [word for word in self.ACCESSORY_WORDS if word in text]
        return {
            "hair": first_character.get("hair") or character_hints.get("hair") or self._hair(text),
            "hair_color": self._first_color_before(text, "hair"),
            "eye_color": self._first_color_before(text, "eyes"),
            "skin": self._skin(text),
            "outfit": first_character.get("outfit")
            or character_hints.get("outfit")
            or self._outfit(text),
            "accessories": self._unique(
                [*hint_accessories, *character_accessories, *objects, *parsed_accessories]
            ),
        }

    def _style(self, text, style=None):
        style = style or {}
        keywords = style.get("keywords") or []
        rendering = style.get("rendering") or ""
        anime = 0.92 if "anime" in text else 0.72 if "webtoon" in text else 0.35
        if any("anime" in str(item).lower() for item in keywords):
            anime = max(anime, 0.92)
        realism = 0.86 if "realistic" in text or "photo" in text else 0.11 if anime > 0.7 else 0.45
        lineart = 0.87 if "line art" in text or "webtoon" in text or "anime" in text else 0.3
        if rendering:
            pass
        elif "webtoon" in text:
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

    def _composition(self, text, scene_plan, composition_hints, composition=None):
        composition = composition or {}
        camera = (
            composition.get("camera")
            or composition_hints.get("camera")
            or scene_plan.get("camera_view")
            or ""
        )
        if not camera:
            if "close up" in text or "close-up" in text:
                camera = "close_up"
            elif "full body" in text:
                camera = "full_body"
            elif "portrait" in text:
                camera = "medium"
            else:
                camera = "eye_level"

        framing = (
            composition.get("framing")
            or composition_hints.get("framing")
            or scene_plan.get("layout_type")
            or ""
        )
        if not framing:
            if "photobooth" in text:
                framing = "photobooth strip"
            elif "poster" in text:
                framing = "poster"
            elif "portrait" in text:
                framing = "portrait"
            else:
                framing = "single subject"

        viewpoint = composition.get("viewpoint") or composition_hints.get("viewpoint") or ""
        if not viewpoint:
            if "side view" in text:
                viewpoint = "side"
            elif "above" in text:
                viewpoint = "slightly_above"
            else:
                viewpoint = "front"

        return {
            "camera": camera,
            "framing": framing,
            "viewpoint": viewpoint,
        }

    def _colors(self, text, color_hints, colors=None):
        colors = colors or {}
        dominant = self._unique(
            [
                *(colors.get("dominant") or []),
                *(color_hints.get("dominant") or []),
                *[color for color in self.COLOR_WORDS if color in text],
            ]
        )
        accent = [
            color
            for color in self._unique(
                [*(colors.get("accent") or []), *(color_hints.get("accent") or []), *dominant]
            )
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

    def _unique(self, values):
        result = []
        seen = set()
        for value in values:
            key = str(value).lower()
            if value and key not in seen:
                result.append(value)
                seen.add(key)
        return result

    def _stringify(self, value):
        if isinstance(value, dict):
            return " ".join(self._stringify(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(self._stringify(item) for item in value)
        return str(value or "")

    def _contains_word(self, text, words):
        normalized = text.replace("-", " ").replace("_", " ")
        tokens = {token.strip(".,:;()[]{}") for token in normalized.split()}
        return any(word in tokens for word in words)
