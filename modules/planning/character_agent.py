class CharacterAgent:
    def run(self, caption: str, user_prompt: str, context: dict | None = None) -> dict:
        print("[CharacterAgent] Running...")
        text = f"{caption or ''} {user_prompt or ''}".lower()
        context = context or {}
        character_inputs = self._get_character_inputs(context)
        character_count = self._infer_character_count(text, character_inputs)
        multi_character_mode = character_count > 1

        characters = [
            self._build_character(index, caption, text, character_inputs)
            for index in range(character_count)
        ]

        character_section = {
            "character_count": character_count,
            "characters": characters,
            "global_character_rules": [
                "Each uploaded image represents one separate character",
                "Do not merge characters",
                "Preserve recognizable identity",
                (
                    "Preserve original outfit, hairstyle, silhouette, "
                    "proportions, visual vibe, and color balance"
                ),
            ],
        }
        print(f"[CharacterAgent] Character count: {character_count}")
        print(f"[CharacterAgent] Multi-character mode: {multi_character_mode}")
        print(f"[CharacterAgent] Character section: {character_section}")
        return character_section

    def _get_character_inputs(self, context):
        for key in ("character_inputs", "reference_images"):
            value = context.get(key)
            if isinstance(value, list) and value:
                return value
        image = context.get("image")
        if isinstance(image, list) and image:
            return image
        return []

    def _infer_character_count(self, text, character_inputs):
        if character_inputs:
            return max(1, len(character_inputs))

        multi_hints = ("2명", "two characters", "two people", "couple", "friends")
        group_hints = ("group", "photobooth")
        if any(hint in text for hint in multi_hints):
            return 2
        if any(hint in text for hint in group_hints):
            return 2
        return 1

    def _build_character(self, index, caption, text, character_inputs):
        caption_hint = self._caption_hint(index, caption, character_inputs)
        return {
            "character_id": f"character_{index + 1}",
            "name": "unknown",
            "gender_hint": self._detect_gender(text),
            "caption_hint": caption_hint,
            "identity_rule": "preserve recognizable identity",
            "outfit_rule": "do not redesign outfit",
            "hair_rule": "do not change hairstyle",
            "silhouette_rule": "preserve original silhouette and proportions",
            "merge_rule": "do not merge with other characters",
        }

    def _caption_hint(self, index, caption, character_inputs):
        if character_inputs:
            item = character_inputs[index] if index < len(character_inputs) else None
            if isinstance(item, dict):
                return item.get("caption") or item.get("caption_hint") or str(caption)
            return f"reference image {index + 1}"
        return str(caption or "main character")

    def _build_subject(self, caption, text):
        subject = str(caption or "").strip() or "main character"
        if "sword" in text and "sword" not in subject.lower():
            subject = f"{subject} holding a sword"
        return subject

    def _detect_gender(self, text):
        if any(word in text for word in ("girl", "woman", "female", "princess")):
            return "female"
        if any(word in text for word in ("boy", "man", "male", "prince")):
            return "male"
        return "unknown"

    def _detect_keyword(self, text, candidates):
        for candidate in candidates:
            if candidate in text:
                return candidate
        return "unspecified"
