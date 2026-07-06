class CharacterProgramBuilder:
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
        print("[CharacterProgramBuilder] Running...")
        state = state or {}
        caption = str(state.get("caption") or "")
        vision_result = state.get("vision_result") or self._vision_result_from_caption(
            state.get("caption")
        )
        reference_image = state.get("reference_image") or {}
        user_prompt = str(state.get("user_prompt") or "")
        scene_plan = state.get("scene_plan") or {}
        text = " ".join(
            [
                caption,
                self._stringify(reference_image),
                str(vision_result.get("detailed_description") or ""),
                user_prompt,
            ]
        ).lower()

        identity = self._identity(text, scene_plan, reference_image)
        appearance = self._appearance(text, reference_image)
        style = self._style(text, reference_image)
        pose = self._pose(text, reference_image)
        expression = self._expression(text, reference_image)
        dominant_colors = self._dominant_colors(text, reference_image)
        identity_rules = self._identity_rules(identity, appearance, text)
        identity_rules = self._unique(
            [
                *identity_rules,
                *((reference_image.get("identity_rules") or []) if reference_image else []),
            ]
        )

        character_program = {
            "identity": identity,
            "appearance": appearance,
            "style": style,
            "pose": pose,
            "expression": expression,
            "dominant_colors": dominant_colors,
            "identity_rules": identity_rules,
        }

        print(f"[CharacterProgramBuilder] Gender: {identity.get('gender')}")
        print(f"[CharacterProgramBuilder] Outfit: {appearance.get('outfit')}")
        print(f"[CharacterProgramBuilder] Accessories: {appearance.get('accessories')}")
        return {"character_program": character_program}

    def _vision_result_from_caption(self, caption):
        return getattr(caption, "vision_result", {}) or {}

    def _identity(self, text, scene_plan, reference_image=None):
        reference_identity = (reference_image or {}).get("identity") or {}
        gender = reference_identity.get("gender") or ""
        if any(word in text for word in ("woman", "girl", "female", "lady")):
            gender = gender or "female"
        elif any(word in text for word in ("man", "boy", "male", "gentleman")):
            gender = gender or "male"

        estimated_age = reference_identity.get("estimated_age") or "adult"
        if any(word in text for word in ("girl", "boy", "child", "kid")):
            estimated_age = "young"
        elif any(word in text for word in ("elderly", "old", "senior")):
            estimated_age = "senior"

        species = reference_identity.get("species") or "human"
        if any(word in text for word in ("cat", "dog", "animal", "creature")):
            species = "non-human"

        role = reference_identity.get("role") or scene_plan.get("scene_type") or ""
        if "sword" in text or "armor" in text:
            role = role or "warrior"
        elif "school" in text or "student" in text:
            role = role or "student"
        elif "princess" in text:
            role = role or "princess"

        return {
            "gender": gender,
            "estimated_age": estimated_age,
            "species": species,
            "role": role,
        }

    def _appearance(self, text, reference_image=None):
        reference_appearance = (reference_image or {}).get("appearance") or {}
        hair_color = self._first_color_before(text, "hair")
        hair = "long hair" if "long hair" in text else "short hair" if "short hair" in text else ""
        eye_color = self._first_color_before(text, "eyes")
        skin = "pale skin" if "pale skin" in text else "dark skin" if "dark skin" in text else ""
        outfit = self._outfit(text)
        accessories = self._unique(
            [
                *(reference_appearance.get("accessories") or []),
                *[word for word in self.ACCESSORY_WORDS if word in text],
            ]
        )

        return {
            "hair": reference_appearance.get("hair") or hair,
            "hair_color": reference_appearance.get("hair_color") or hair_color,
            "eye_color": reference_appearance.get("eye_color") or eye_color,
            "skin": reference_appearance.get("skin") or skin,
            "outfit": reference_appearance.get("outfit") or outfit,
            "accessories": accessories,
        }

    def _style(self, text, reference_image=None):
        reference_style = (reference_image or {}).get("style") or {}
        anime = "high" if "anime" in text else "medium" if "webtoon" in text else ""
        realism = "high" if "realistic" in text or "photo" in text else "low" if anime else ""
        rendering = reference_style.get("rendering") or ""
        if "webtoon" in text:
            rendering = rendering or "soft webtoon"
        elif "line art" in text:
            rendering = rendering or "clean line art"
        elif anime:
            rendering = rendering or "anime illustration"
        return {
            "anime": reference_style.get("anime") or anime,
            "realism": reference_style.get("realism") or realism,
            "rendering": rendering,
        }

    def _pose(self, text, reference_image=None):
        reference_pose = (reference_image or {}).get("pose")
        if reference_pose:
            return reference_pose
        if "holding" in text and "sword" in text:
            return "holding a sword"
        if "standing" in text:
            return "standing"
        if "sitting" in text:
            return "sitting"
        if "portrait" in text:
            return "portrait pose"
        return "natural pose"

    def _expression(self, text, reference_image=None):
        reference_expression = (reference_image or {}).get("expression")
        if reference_expression:
            return reference_expression
        if "smile" in text or "smiling" in text:
            return "smiling"
        if "serious" in text:
            return "serious"
        if "sad" in text:
            return "sad"
        return "natural readable expression"

    def _dominant_colors(self, text, reference_image=None):
        reference_colors = ((reference_image or {}).get("colors") or {}).get("dominant") or []
        return self._unique([*reference_colors, *[color for color in self.COLOR_WORDS if color in text]])

    def _identity_rules(self, identity, appearance, text):
        rules = ["preserve recognizable character identity"]
        if identity.get("gender"):
            rules.append(f"keep {identity['gender']} identity cues")
        if appearance.get("outfit"):
            rules.append(f"preserve outfit: {appearance['outfit']}")
        if appearance.get("accessories"):
            rules.append(
                "preserve accessories: "
                + ", ".join(appearance.get("accessories", [])[:3])
            )
        if "caption" in text:
            rules.append("stay faithful to source caption")
        return rules

    def _first_color_before(self, text, noun):
        for color in self.COLOR_WORDS:
            if f"{color} {noun}" in text:
                return color
        return ""

    def _outfit(self, text):
        for color in self.COLOR_WORDS:
            for noun in ("clothes", "robe", "dress", "shirt", "armor", "outfit"):
                phrase = f"{color} {noun}"
                if phrase in text:
                    return phrase
        if "robe" in text:
            return "robe"
        if "dress" in text:
            return "dress"
        if "armor" in text:
            return "armor"
        return ""

    def _stringify(self, value):
        if isinstance(value, dict):
            return " ".join(self._stringify(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(self._stringify(item) for item in value)
        return str(value or "")

    def _unique(self, values):
        result = []
        seen = set()
        for value in values:
            key = str(value).lower()
            if value and key not in seen:
                result.append(value)
                seen.add(key)
        return result
