class NegativePromptAgent:
    def run(self, user_prompt: str, retrieved_context: dict | None = None) -> dict:
        print("[NegativePromptAgent] Running...")
        negatives = []

        for item in retrieved_context.get("negative", []) if retrieved_context else []:
            self._append_unique(negatives, item)

        for item in ("blurry", "bad anatomy", "low quality", "duplicate"):
            self._append_unique(negatives, item)

        for item in ("concept art sheet", "character lineup", "weapon showcase"):
            if item in str(user_prompt or "").lower():
                self._append_unique(negatives, item)

        return {"negative_prompt": negatives[:8]}

    def _append_unique(self, values, value):
        if value and value not in values:
            values.append(value)
