class PlannerAgent:
    def run(self, user_prompt: str, image_provided: bool) -> dict:
        print("[PlannerAgent] Running...")

        execution_plan = [
            "memory_load",
            "vision",
            "retrieval",
            "prompt_compressor",
            "scene_planning",
            "character",
            "style",
            "layout",
            "pose",
            "expression",
            "lighting",
            "negative_prompt",
            "prompt_assembler",
            "generation",
            "evaluation",
            "reflection",
            "retry",
            "memory_save",
        ]

        result = {
            "task_type": (
                "multi_character_image_generation"
                if self._has_multi_character_hint(user_prompt)
                else "image_generation"
            ),
            "requires_vision": image_provided,
            "requires_generation": True,
            "requires_evaluation": True,
            "requires_retry": True,
            "execution_plan": execution_plan,
            "reason": self._build_reason(user_prompt, image_provided),
        }

        print(f"[PlannerAgent] Execution plan: {execution_plan}")
        return result

    def _build_reason(self, user_prompt, image_provided):
        has_prompt = bool(user_prompt and user_prompt.strip())
        if self._has_multi_character_hint(user_prompt):
            return (
                "Prompt includes possible multi-character reference intent, so "
                "character reference preservation should be considered."
            )

        if image_provided and has_prompt:
            return (
                "Image and prompt are provided, so full multimodal generation "
                "workflow is selected."
            )
        if image_provided:
            return (
                "Image is provided, so vision-based generation workflow is "
                "selected."
            )
        if has_prompt:
            return (
                "Prompt is provided without an image, so text-guided generation "
                "workflow is selected."
            )
        return "No specific input is provided, so default generation workflow is selected."

    def _has_multi_character_hint(self, user_prompt):
        text = str(user_prompt or "").lower()
        hints = ("2명", "two", "friends", "group", "photobooth", "couple")
        return any(hint in text for hint in hints)
