class LightingAgent:
    def run(self, user_prompt: str, retrieved_context: dict | None = None) -> dict:
        print("[LightingAgent] Running...")
        lighting = []
        text = str(user_prompt or "").lower()

        for item in retrieved_context.get("lighting", []) if retrieved_context else []:
            self._append_unique(lighting, item)

        for keyword in ("cinematic lighting", "soft shadow", "warm tone"):
            if keyword in text or keyword.split()[0] in text:
                self._append_unique(lighting, keyword)

        if not lighting:
            lighting = ["cinematic lighting", "soft shadow"]
        return {"lighting_keywords": lighting[:3]}

    def _append_unique(self, values, value):
        if value and value not in values:
            values.append(value)
