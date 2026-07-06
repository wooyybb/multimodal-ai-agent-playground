class StyleAgent:
    def run(self, user_prompt: str, retrieved_context: dict | None = None) -> dict:
        print("[StyleAgent] Running...")
        styles = []
        text = str(user_prompt or "").lower()

        for style in retrieved_context.get("style", []) if retrieved_context else []:
            self._append_unique(styles, style)

        for keyword in ("anime", "soft webtoon", "clean line art", "pastel color"):
            if keyword in text or (keyword == "soft webtoon" and "webtoon" in text):
                self._append_unique(styles, keyword)

        if not styles:
            styles = ["soft Korean webtoon-style illustration", "clean anime-style coloring"]
        return {
            "style_keywords": styles[:4],
            "rendering_rules": [
                "lightweight anime lineart",
                "soft pastel-friendly tones",
            ],
        }

    def _append_unique(self, values, value):
        if value and value not in values:
            values.append(value)
