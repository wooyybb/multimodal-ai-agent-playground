class PlannerAgent:
    def run(self, user_prompt: str, image_provided: bool) -> dict:
        print("[PlannerAgent] Running...")

        execution_plan = [
            "memory_load",
            "vision",
            "retrieval",
            "prompt_compressor",
            "prompt",
            "generation",
            "evaluation",
            "reflection",
            "retry",
            "memory_save",
        ]

        result = {
            "task_type": "image_generation",
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
