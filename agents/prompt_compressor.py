class PromptCompressor:
    def run(self, context: dict) -> dict:
        print("[PromptCompressor] Running...")

        try:
            context = context or {}
            planner_result = context.get("planner_result") or {}
            previous_best_score = context.get("previous_best_score")
            previous_best_prompt = context.get("previous_best_prompt")
            retry_history = context.get("retry_history") or []
            style_preferences = context.get("style_preferences")

            compressed_context = {
                "task": planner_result.get("task_type", "image_generation"),
                "quality_hint": "high quality",
                "planner_hint": self._compress_planner_hint(planner_result),
            }

            if previous_best_prompt:
                compressed_context["style_hint"] = (
                    "maintain previous successful style"
                )

            if previous_best_score is not None:
                compressed_context["history_hint"] = self._compress_history_hint(
                    previous_best_score
                )

            if retry_history:
                compressed_context["retry_hint"] = "retry-aware"

            style_hint = self._compress_style_preferences(style_preferences)
            if style_hint:
                compressed_context["style_keyword"] = style_hint

            print(
                "[PromptCompressor] Compressed context keys: "
                f"{list(compressed_context.keys())}"
            )
            return compressed_context
        except Exception as error:
            print(f"[PromptCompressor] Error: {error}")
            return {}

    def _compress_planner_hint(self, planner_result):
        reason = str(planner_result.get("reason", "")).lower()
        if "full multimodal" in reason:
            return "full workflow"
        if "vision" in reason:
            return "vision-guided workflow"
        if "text-guided" in reason:
            return "text-guided workflow"
        return "standard workflow"

    def _compress_history_hint(self, score):
        try:
            score = float(score)
        except (TypeError, ValueError):
            return "previous attempt available"

        if score >= 0.75:
            return "previous attempt successful"
        return "previous attempt needs improvement"

    def _compress_style_preferences(self, style_preferences):
        if not style_preferences:
            return None

        if isinstance(style_preferences, (list, tuple)):
            return ", ".join(str(item).strip() for item in style_preferences[:3] if item)

        style_text = str(style_preferences).replace("\n", " ").strip()
        if not style_text:
            return None
        return " ".join(style_text.split()[:5])
