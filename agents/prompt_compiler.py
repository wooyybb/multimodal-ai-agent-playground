from generation.reference_conditioning import ReferenceConditioningBuilder


class PromptCompiler:
    INTERNAL_TERMS = (
        "context_program",
        "agent trace",
        "debug",
        "internal context",
        "prompt quality score",
    )
    CLIP_REMOVE_TERMS = (
        "masterpiece",
        "8k",
        "ultra detailed",
        "ultra-detailed",
        "best quality",
        "high quality",
        "low quality",
        "negative",
        "bad anatomy",
        "blurry",
    )

    def run(self, state: dict) -> dict:
        print("[PromptCompiler] Running...")
        state = state or {}
        provider = self._provider(state)
        context_program = state.get("context_program") or {}
        context_reasoning = state.get("context_reasoning") or {}
        context_validation = state.get("context_validation") or {}
        prompt_sections = state.get("prompt_sections") or {}
        negative_prompt = state.get("negative_prompt") or ""

        print(f"[PromptCompiler] Provider: {provider}")
        prompt_blocks = self._build_prompt_blocks(
            context_program,
            context_reasoning,
            prompt_sections,
        )
        negative = self._negative_prompt(context_program, negative_prompt)

        if provider == "gpt_image":
            generation_prompt, notes, target_words = self._compile_gpt_image(prompt_blocks)
        elif provider == "sdxl":
            generation_prompt, notes, target_words = self._compile_sdxl(prompt_blocks)
        else:
            generation_prompt, notes, target_words = self._compile_flux(prompt_blocks)
            provider = "flux"

        if context_validation and context_validation.get("valid") is False:
            notes.append("context validation reported invalid context")
        if negative and provider == "flux":
            notes.append("negative prompt preserved in package but not directly used by FLUX generation")

        rendered_prompts = self._render_prompts(
            generation_prompt,
            negative,
            prompt_blocks,
            context_program,
            context_reasoning,
        )
        reference_conditioning = ReferenceConditioningBuilder().build(state)
        package = {
            "provider": provider,
            "positive_prompt": rendered_prompts["generation_prompt"],
            "negative_prompt": negative,
            "prompt_blocks": prompt_blocks,
            "prompt_rendering": rendered_prompts,
            "reference_conditioning_package": reference_conditioning,
            "compiler_notes": notes,
            "prompt_budget": {
                "target_words": target_words,
                "actual_words": len(rendered_prompts["generation_prompt"].split()),
            },
        }

        print(f"[PromptCompiler] Positive prompt word count: {package['prompt_budget']['actual_words']}")
        print(f"[PromptCompiler] CLIP prompt word count: {len(rendered_prompts['clip_prompt'].split())}")
        print(f"[PromptCompiler] Compiler notes: {notes}")
        return {
            "compiled_prompt_package": package,
            "reference_conditioning_package": reference_conditioning,
            "prompt_rendering": rendered_prompts,
            **rendered_prompts,
        }

    def _provider(self, state):
        routing = state.get("provider_routing") or {}
        return str(
            state.get("provider")
            or routing.get("selected_provider")
            or routing.get("fallback_provider")
            or "flux"
        ).lower()

    def _build_prompt_blocks(self, context_program, context_reasoning, prompt_sections):
        scene = context_program.get("scene") or {}
        characters = context_program.get("characters") or {}
        style = context_program.get("style") or {}
        layout = context_program.get("layout") or {}
        pose = context_program.get("pose") or {}
        expression = context_program.get("expression") or {}
        lighting = context_program.get("lighting") or {}
        quality = context_program.get("quality") or {}

        return {
            "subject": self._join_parts(
                [
                    self._character_phrase(characters),
                    (prompt_sections.get("character") or {}).get("summary"),
                ]
            ),
            "scene": self._join_parts(
                [
                    scene.get("narrative"),
                    scene.get("interaction"),
                    context_reasoning.get("scene_goal"),
                    context_reasoning.get("interaction_goal"),
                ]
            ),
            "style": self._join_parts(
                [
                    style.get("style_keywords", []),
                    style.get("rendering_rules", []),
                    context_reasoning.get("style_goal"),
                ]
            ),
            "layout": self._join_parts(
                [
                    layout.get("layout_type"),
                    layout.get("aspect_ratio"),
                    layout.get("frame_structure"),
                    layout.get("camera_view"),
                    layout.get("subject_placement"),
                    layout.get("composition_rules", []),
                    context_reasoning.get("composition_goal"),
                ]
            ),
            "lighting": self._join_parts(
                [
                    lighting.get("lighting_keywords", []),
                    lighting.get("mood"),
                ]
            ),
            "quality": self._join_parts(
                [
                    quality.get("quality_keywords", []),
                    pose.get("pose_rules", []),
                    expression.get("expression_rules", []),
                ]
            ),
        }

    def _compile_flux(self, prompt_blocks):
        prompt = self._join_parts(
            [
                prompt_blocks.get("subject"),
                prompt_blocks.get("scene"),
                prompt_blocks.get("style"),
                prompt_blocks.get("layout"),
                prompt_blocks.get("lighting"),
                prompt_blocks.get("quality"),
            ]
        )
        prompt = self._clean_prompt(prompt)
        prompt = self._limit_words(prompt, 110)
        return prompt, ["compiled dense FLUX visual prompt"], 100

    def _compile_sdxl(self, prompt_blocks):
        prompt = self._join_parts(
            [
                prompt_blocks.get("subject"),
                prompt_blocks.get("style"),
                prompt_blocks.get("layout"),
                prompt_blocks.get("lighting"),
                prompt_blocks.get("quality"),
            ]
        )
        prompt = self._clean_prompt(prompt)
        prompt = self._limit_words(prompt, 130)
        return prompt, ["compiled SDXL skeleton positive prompt"], 120

    def _compile_gpt_image(self, prompt_blocks):
        lines = [
            "Create an image using this structured visual brief.",
            f"Subject: {prompt_blocks.get('subject')}",
            f"Scene: {prompt_blocks.get('scene')}",
            f"Style: {prompt_blocks.get('style')}",
            f"Layout: {prompt_blocks.get('layout')}",
            f"Lighting: {prompt_blocks.get('lighting')}",
            f"Quality: {prompt_blocks.get('quality')}",
        ]
        prompt = self._clean_prompt(" ".join(line for line in lines if line.strip()))
        return prompt, ["compiled GPT Image structured instruction"], 180

    def _negative_prompt(self, context_program, fallback):
        negative = context_program.get("negative") or {}
        return self._join_parts(
            [
                fallback,
                negative.get("negative_prompt", []),
                negative.get("strict_avoid", []),
            ]
        )

    def _character_phrase(self, characters):
        count = characters.get("character_count") or 1
        items = characters.get("characters") or []
        hints = [
            item.get("caption_hint")
            for item in items
            if isinstance(item, dict) and item.get("caption_hint")
        ]
        rules = characters.get("preservation_rules") or []
        return self._join_parts([f"{count} recognizable subject", hints[:3], rules[:2]])

    def _render_prompts(
        self,
        generation_prompt,
        negative_prompt,
        prompt_blocks,
        context_program,
        context_reasoning,
    ):
        clip_prompt = self._render_clip_prompt(prompt_blocks)
        pickscore_prompt = self._render_pickscore_prompt(prompt_blocks)
        vlm_judge_prompt = self._render_vlm_judge_prompt(
            prompt_blocks,
            context_program,
            context_reasoning,
        )
        return {
            "generation_prompt": generation_prompt,
            "clip_prompt": clip_prompt,
            "pickscore_prompt": pickscore_prompt,
            "vlm_judge_prompt": vlm_judge_prompt,
            "negative_prompt": negative_prompt,
        }

    def _render_clip_prompt(self, prompt_blocks):
        semantic = self._join_parts(
            [
                prompt_blocks.get("subject"),
                prompt_blocks.get("scene"),
                prompt_blocks.get("layout"),
            ]
        )
        semantic = self._clean_clip_prompt(semantic)
        return self._limit_words(semantic, 40)

    def _render_pickscore_prompt(self, prompt_blocks):
        prompt = self._join_parts(
            [
                prompt_blocks.get("subject"),
                prompt_blocks.get("style"),
                prompt_blocks.get("layout"),
                prompt_blocks.get("lighting"),
                prompt_blocks.get("quality"),
                "appealing composition",
                "coherent style",
                "aesthetic visual balance",
            ]
        )
        return self._clean_prompt(prompt)

    def _render_vlm_judge_prompt(self, prompt_blocks, context_program, context_reasoning):
        criteria = (
            "Compare the reference image and generated image. "
            "Evaluate identity, style, lighting, camera, composition, background, "
            "and prompt alignment. Return an evidence-based visual judgment."
        )
        prompt = self._join_parts(
            [
                criteria,
                f"Subject: {prompt_blocks.get('subject')}",
                f"Scene: {prompt_blocks.get('scene')}",
                f"Style: {prompt_blocks.get('style')}",
                f"Layout: {prompt_blocks.get('layout')}",
                f"Lighting: {prompt_blocks.get('lighting')}",
                f"Quality: {prompt_blocks.get('quality')}",
                f"Reference context: {context_program.get('reference_image') or {}}",
                f"Reasoning context: {context_reasoning}",
            ]
        )
        return self._clean_prompt(prompt)

    def _clean_clip_prompt(self, prompt):
        cleaned = str(prompt or "")
        for term in self.CLIP_REMOVE_TERMS:
            cleaned = cleaned.replace(term, "")
            cleaned = cleaned.replace(term.title(), "")
            cleaned = cleaned.replace(term.upper(), "")
        return self._clean_prompt(cleaned)

    def _join_parts(self, values):
        parts = []
        self._append_value(parts, values)
        parts = [str(part).strip() for part in parts if str(part).strip()]
        return ", ".join(parts)

    def _append_value(self, parts, value):
        if value is None:
            return
        if isinstance(value, str):
            if value.strip():
                parts.append(value)
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                self._append_value(parts, item)
            return
        if isinstance(value, dict):
            for item in value.values():
                self._append_value(parts, item)
            return
        parts.append(value)

    def _clean_prompt(self, prompt):
        cleaned = str(prompt or "").replace("\n", " ")
        for term in self.INTERNAL_TERMS:
            cleaned = cleaned.replace(term, "")
        phrases = []
        seen = set()
        for phrase in cleaned.split(","):
            item = " ".join(phrase.split()).strip(" ,.")
            key = item.lower()
            if item and key not in seen:
                phrases.append(item)
                seen.add(key)
        return ", ".join(phrases)

    def _limit_words(self, prompt, max_words):
        words = str(prompt or "").split()
        if len(words) <= max_words:
            return prompt
        return " ".join(words[:max_words]).rstrip(" ,.")
