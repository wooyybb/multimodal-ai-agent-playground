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
            retrieved_context = context.get("retrieved_context") or {}

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

            retrieved_hints = self._compress_retrieved_context(retrieved_context)
            compressed_context.update(retrieved_hints)

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

    def _compress_retrieved_context(self, retrieved_context):
        if not isinstance(retrieved_context, dict):
            return {}

        hints = {}
        style = self._pick_keywords(retrieved_context.get("style"), limit=2)
        lighting = self._pick_keywords(retrieved_context.get("lighting"), limit=2)
        composition = self._pick_keywords(
            retrieved_context.get("composition"),
            limit=1,
        )
        quality = self._pick_keywords(retrieved_context.get("quality"), limit=2)
        negative = self._pick_keywords(retrieved_context.get("negative"), limit=3)

        if style:
            hints["retrieved_style_hint"] = style
        if lighting:
            hints["retrieved_lighting_hint"] = lighting
        if composition:
            hints["retrieved_composition_hint"] = composition
        if quality:
            hints["retrieved_quality_hint"] = quality
        if negative:
            hints["negative_prompt_hint"] = negative

        return hints

    def _pick_keywords(self, values, limit):
        if not values:
            return None
        if not isinstance(values, (list, tuple)):
            values = [values]

        keywords = []
        for value in values:
            text = str(value).replace("\n", " ").strip()
            if text and text not in keywords:
                keywords.append(text)
            if len(keywords) >= limit:
                break

        if not keywords:
            return None
        return ", ".join(keywords)

    def compress_prompt(
        self,
        prompt: str,
        max_words: int = 40,
        label: str = "retry",
    ) -> str:
        print(f"[PromptCompressor] Compressing {label} prompt...")

        prompt = str(prompt or "").replace("\n", " ").strip()
        words = prompt.split()

        if len(words) > max_words:
            prompt = " ".join(words[:max_words]).rstrip(" ,.")

        print(
            f"[PromptCompressor] {label.capitalize()} prompt word count: "
            f"{len(prompt.split())}"
        )
        return prompt

    def make_evaluation_prompt(
        self,
        caption: str,
        user_prompt: str,
        prompt: str | None = None,
    ) -> str:
        print("[PromptCompressor] Building CLIP-safe evaluation prompt...")

        caption_part = self._first_words(caption, limit=12)
        user_part = self._first_words(user_prompt, limit=8)
        source_text = f"{user_prompt or ''} {prompt or ''}".lower()

        style_keywords = self._extract_known_keywords(
            source_text,
            [
                "anime",
                "realistic",
                "ghibli",
                "pixel art",
                "oil painting",
                "cinematic",
                "portrait",
                "landscape",
            ],
            limit=3,
        )
        quality_keywords = self._extract_known_keywords(
            source_text,
            ["high quality", "best quality", "masterpiece", "detailed", "clean"],
            limit=2,
        )

        parts = []
        if caption_part:
            parts.append(caption_part)
        if user_part:
            parts.append(user_part)
        parts.extend(style_keywords)
        parts.extend(quality_keywords or ["high quality"])

        evaluation_prompt = ", ".join(self._deduplicate(parts))
        evaluation_prompt = self.compress_prompt(
            evaluation_prompt,
            max_words=40,
            label="evaluation",
        )
        return evaluation_prompt

    def _first_words(self, text, limit):
        words = str(text or "").replace("\n", " ").strip().split()
        return " ".join(words[:limit])

    def _extract_known_keywords(self, text, candidates, limit):
        matches = []
        for candidate in candidates:
            if candidate in text and candidate not in matches:
                matches.append(candidate)
            if len(matches) >= limit:
                break
        return matches

    def _deduplicate(self, values):
        result = []
        for value in values:
            if value and value not in result:
                result.append(value)
        return result
