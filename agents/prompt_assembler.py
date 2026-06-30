class PromptAssembler:
    def run(
        self,
        caption,
        user_prompt,
        character_section,
        style_section,
        layout_section,
        pose_section,
        expression_section,
        negative_section,
        compressed_context=None,
    ) -> dict:
        print("[PromptAssembler] Building generation prompt...")

        character_bits = self._dict_values(character_section)
        style_bits = (style_section or {}).get("style_keywords", [])
        rendering_bits = (style_section or {}).get("rendering_rules", [])
        layout_bits = self._dict_values(layout_section)
        pose_bits = (pose_section or {}).get("pose_rules", [])
        expression_bits = (expression_section or {}).get("expression_rules", [])
        lighting_bits = (compressed_context or {}).get("retrieved_lighting_hint")
        negative_prompt = ", ".join((negative_section or {}).get("negative_prompt", []))

        parts = [
            "high quality",
            f"detailed image of {caption}",
            ", ".join(character_bits),
            ", ".join(style_bits),
            ", ".join(rendering_bits),
            ", ".join(layout_bits),
            ", ".join(pose_bits),
            ", ".join(expression_bits),
            lighting_bits,
        ]

        if user_prompt and str(user_prompt).strip():
            parts.append(f"user request: {str(user_prompt).strip()}")

        generation_prompt = ", ".join(part for part in parts if part)
        generation_prompt = self._limit_words(generation_prompt, max_words=120)

        result = {
            "generation_prompt": generation_prompt,
            "negative_prompt": negative_prompt,
            "prompt_sections": {
                "character": character_section,
                "style": style_section,
                "layout": layout_section,
                "pose": pose_section,
                "expression": expression_section,
            },
        }
        print(f"[PromptAssembler] Generation prompt: {generation_prompt}")
        print(f"[PromptAssembler] Negative prompt: {negative_prompt}")
        return result

    def _limit_words(self, prompt, max_words):
        words = prompt.split()
        if len(words) <= max_words:
            return prompt
        return " ".join(words[:max_words]).rstrip(" ,.")

    def _dict_values(self, section):
        values = []
        for value in (section or {}).values():
            if isinstance(value, list):
                values.extend(value)
            elif value:
                values.append(str(value))
        return values
