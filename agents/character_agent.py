class CharacterAgent:
    def run(self, caption: str, user_prompt: str, context: dict | None = None) -> dict:
        print("[CharacterAgent] Running...")
        text = f"{caption or ''} {user_prompt or ''}".lower()

        character_section = {
            "subject": self._build_subject(caption, text),
            "gender_hint": self._detect_gender(text),
            "outfit_hint": self._detect_keyword(
                text,
                ["white clothes", "white robe", "school uniform", "dress", "armor"],
            ),
            "identity_rule": "preserve recognizable character identity",
            "silhouette_rule": "preserve original silhouette and proportions",
        }
        print(f"[CharacterAgent] Character section: {character_section}")
        return character_section

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
