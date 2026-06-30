class PromptAgent:
    def run(self, caption: str, user_prompt: str, context: dict | None = None) -> str:
        print("[PromptAgent] Running...")
        print(f"[PromptAgent] Caption: {caption}")
        print(f"[PromptAgent] User Prompt: {user_prompt}")
        context = context or {}
        print(f"[PromptAgent] Context keys: {list(context.keys())}")

        try:
            base_prompt = (
                f"high quality, detailed image of {caption}, cinematic lighting"
            )

            if user_prompt.strip():
                final_prompt = f"{base_prompt}, user request: {user_prompt.strip()}"
            else:
                final_prompt = base_prompt

            context_notes = self._build_context_notes(context)
            if context_notes:
                final_prompt = f"{final_prompt}, {context_notes}"

            final_prompt = self._limit_prompt(final_prompt)
        except Exception:
            final_prompt = self._fallback_prompt(caption, user_prompt)

        print(f"[PromptAgent] Final Prompt: {final_prompt}")
        return final_prompt

    def _build_context_notes(self, context):
        notes = []

        planner_result = context.get("planner_result") or {}
        task_type = planner_result.get("task_type")
        reason = planner_result.get("reason")
        if task_type:
            notes.append(f"task type: {task_type}")
        if reason:
            notes.append(f"planning note: {self._shorten(reason, 90)}")

        previous_best_prompt = context.get("previous_best_prompt")
        if previous_best_prompt:
            notes.append(
                "inspired by previous successful prompt: "
                f"{self._shorten(previous_best_prompt, 120)}"
            )

        previous_best_score = context.get("previous_best_score")
        if previous_best_score is not None:
            notes.append(f"previous best score reference: {previous_best_score}")

        return ", ".join(notes)

    def _fallback_prompt(self, caption, user_prompt):
        base_prompt = f"high quality, detailed image of {caption}, cinematic lighting"
        if user_prompt and user_prompt.strip():
            return f"{base_prompt}, user request: {user_prompt.strip()}"
        return base_prompt

    def _limit_prompt(self, prompt, max_length=500):
        if len(prompt) <= max_length:
            return prompt
        return prompt[: max_length - 3].rstrip() + "..."

    def _shorten(self, text, max_length):
        text = str(text).replace("\n", " ").strip()
        if len(text) <= max_length:
            return text
        return text[: max_length - 3].rstrip() + "..."
