class PromptAgent:
    def run(
        self,
        caption: str,
        user_prompt: str,
        compressed_context: dict | None = None,
        context: dict | None = None,
    ) -> str:
        print("[PromptAgent] Running...")
        print(f"[PromptAgent] Caption: {caption}")
        print(f"[PromptAgent] User Prompt: {user_prompt}")
        compressed_context = compressed_context or {}
        print(
            "[PromptAgent] Compressed context keys: "
            f"{list(compressed_context.keys())}"
        )

        try:
            quality = compressed_context.get("quality_hint") or "high quality"
            style_parts = ["cinematic lighting"]
            style_keyword = compressed_context.get("style_keyword")
            if style_keyword:
                style_parts.append(style_keyword)

            final_prompt_parts = [
                quality,
                f"detailed image of {caption}",
                ", ".join(style_parts),
            ]

            context_notes = self._build_context_notes(compressed_context)
            if context_notes:
                final_prompt_parts.append(context_notes)

            if user_prompt and user_prompt.strip():
                final_prompt_parts.append(f"user request: {user_prompt.strip()}")

            final_prompt = self._limit_prompt(", ".join(final_prompt_parts))
        except Exception:
            final_prompt = self._fallback_prompt(caption, user_prompt)

        print(f"[PromptAgent] Final Prompt: {final_prompt}")
        return final_prompt

    def _build_context_notes(self, compressed_context):
        notes = []

        for key in (
            "task",
            "planner_hint",
            "style_hint",
            "history_hint",
            "retry_hint",
            "retrieved_style_hint",
            "retrieved_lighting_hint",
            "retrieved_composition_hint",
            "retrieved_quality_hint",
            "negative_prompt_hint",
        ):
            value = compressed_context.get(key)
            if value:
                if key == "negative_prompt_hint":
                    notes.append(f"avoid {value}")
                else:
                    notes.append(str(value))

        return ", ".join(notes)

    def _fallback_prompt(self, caption, user_prompt):
        base_prompt = f"high quality, detailed image of {caption}, cinematic lighting"
        if user_prompt and user_prompt.strip():
            return f"{base_prompt}, user request: {user_prompt.strip()}"
        return base_prompt

    def _limit_prompt(self, prompt, max_words=60, max_length=360):
        words = prompt.split()
        if len(words) > max_words:
            prompt = " ".join(words[:max_words])

        if len(prompt) <= max_length:
            return prompt
        return prompt[: max_length - 3].rstrip() + "..."

    def _shorten(self, text, max_length):
        text = str(text).replace("\n", " ").strip()
        if len(text) <= max_length:
            return text
        return text[: max_length - 3].rstrip() + "..."
