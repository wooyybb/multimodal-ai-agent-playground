class ProviderPromptAdapter:
    INTERNAL_TERMS = {
        "image_generation",
        "full workflow",
        "previous attempt needs improvement",
        "memory hint",
        "planner hint",
        "agent trace",
        "internal context",
    }

    def run(
        self,
        state_or_canonical_prompt,
        negative_prompt: str | None = None,
        provider: str = "flux",
        prompt_sections: dict | None = None,
        scene_plan: dict | None = None,
    ) -> dict:
        if isinstance(state_or_canonical_prompt, dict):
            state = state_or_canonical_prompt
            if state.get("compiled_prompt_package"):
                return self._from_compiled_package(state)
            result = self._run_legacy(
                state.get("canonical_prompt") or state.get("final_prompt", ""),
                negative_prompt=state.get("negative_prompt"),
                provider=state.get("provider", "flux"),
                prompt_sections=state.get("prompt_sections"),
                scene_plan=state.get("scene_plan"),
                context_program=state.get("context_program"),
            )
            provider_prompt = result.get(
                "provider_prompt",
                state.get("canonical_prompt") or state.get("final_prompt", ""),
            )
            return {
                "provider": result.get("provider", "flux"),
                "provider_prompt": provider_prompt,
                "provider_negative_prompt": result.get(
                    "provider_negative_prompt",
                    state.get("negative_prompt") or "",
                ),
                "reference_conditioning_package": state.get(
                    "reference_conditioning_package",
                    result.get("reference_conditioning_package"),
                ),
                "adapter_notes": self._with_optimized_note(
                    self._with_conditioning_note(
                        result.get("adapter_notes", []),
                        state.get("reference_conditioning_package")
                        or result.get("reference_conditioning_package"),
                        result.get("provider", "flux"),
                    ),
                    state,
                ),
                "final_prompt": provider_prompt,
            }

        return self._run_legacy(
            state_or_canonical_prompt,
            negative_prompt=negative_prompt,
            provider=provider,
            prompt_sections=prompt_sections,
            scene_plan=scene_plan,
        )

    def _run_legacy(
        self,
        canonical_prompt: str,
        negative_prompt: str | None = None,
        provider: str = "flux",
        prompt_sections: dict | None = None,
        scene_plan: dict | None = None,
        context_program: dict | None = None,
    ) -> dict:
        print("[ProviderPromptAdapter] Running...")
        provider = (provider or "flux").lower()
        fallback_used = False
        if provider not in {"flux", "gpt_image", "sdxl"}:
            provider = "flux"
            fallback_used = True
        print(f"[ProviderPromptAdapter] Provider: {provider}")

        if provider == "gpt_image":
            result = self._adapt_gpt_image(
                canonical_prompt,
                negative_prompt,
                prompt_sections,
                context_program,
            )
            if fallback_used:
                result["adapter_notes"].append("unknown provider fallback to flux")
            return result
        if provider == "sdxl":
            result = self._adapt_sdxl(canonical_prompt, negative_prompt, context_program)
            if fallback_used:
                result["adapter_notes"].append("unknown provider fallback to flux")
            return result
        result = self._adapt_flux(
            canonical_prompt,
            negative_prompt,
            scene_plan,
            context_program,
        )
        if fallback_used:
            result["adapter_notes"].append("unknown provider fallback to flux")
        return result

    def _from_compiled_package(self, state):
        package = state.get("compiled_prompt_package") or {}
        provider_prompt = package.get("positive_prompt") or state.get("final_prompt") or ""
        provider_negative_prompt = package.get("negative_prompt") or state.get("negative_prompt") or ""
        reference_conditioning = (
            state.get("reference_conditioning_package")
            or package.get("reference_conditioning_package")
        )
        notes = list(package.get("compiler_notes") or [])
        notes.append("used compiled prompt package")
        notes = self._with_conditioning_note(
            notes,
            reference_conditioning,
            package.get("provider") or state.get("provider") or "flux",
        )
        return {
            "provider": package.get("provider") or state.get("provider") or "flux",
            "provider_prompt": provider_prompt,
            "provider_negative_prompt": provider_negative_prompt,
            "reference_conditioning_package": reference_conditioning,
            "adapter_notes": self._with_optimized_note(notes, state),
            "final_prompt": provider_prompt,
        }
        if fallback_used:
            result["adapter_notes"].append("unknown provider fallback to flux")
        return result

    def _adapt_flux(self, canonical_prompt, negative_prompt, scene_plan, context_program=None):
        if context_program:
            print("[ProviderPromptAdapter] Compiling FLUX prompt from context program...")
            prompt = self._compile_flux_from_context(context_program, canonical_prompt)
        else:
            prompt = self._clean_prompt(canonical_prompt)
        prompt = self._deduplicate_phrases(prompt)
        prompt = self._limit_words(prompt, min_words=70, max_words=110)
        print(f"[ProviderPromptAdapter] FLUX prompt word count: {len(prompt.split())}")
        return {
            "provider": "flux",
            "provider_prompt": prompt,
            "provider_negative_prompt": negative_prompt or "",
            "adapter_notes": [
                "compressed for FLUX",
                "removed internal planning terms",
                "kept visual subject, style, layout, pose, expression, composition",
                "used context program" if context_program else "used canonical prompt",
            ],
        }

    def _adapt_gpt_image(
        self,
        canonical_prompt,
        negative_prompt,
        prompt_sections,
        context_program=None,
    ):
        if context_program:
            prompt = self._compile_gpt_image_from_context(context_program, canonical_prompt)
        else:
            prompt = (
                "Create an image using this structured instruction: "
                f"{self._clean_prompt(canonical_prompt)}"
            )
        return {
            "provider": "gpt_image",
            "provider_prompt": prompt,
            "provider_negative_prompt": negative_prompt or "",
            "adapter_notes": [
                "skeleton adapter for GPT Image",
                "structured instruction format",
                "used context program" if context_program else "used canonical prompt",
            ],
            "sections": prompt_sections or {},
        }

    def _adapt_sdxl(self, canonical_prompt, negative_prompt, context_program=None):
        if context_program:
            prompt = self._compile_flux_from_context(context_program, canonical_prompt)
            negative_prompt = self._negative_from_context(context_program, negative_prompt)
        else:
            prompt = self._clean_prompt(canonical_prompt)
        return {
            "provider": "sdxl",
            "provider_prompt": prompt,
            "provider_negative_prompt": negative_prompt or "",
            "adapter_notes": [
                "skeleton adapter for SDXL",
                "separated prompt and negative prompt",
                "used context program" if context_program else "used canonical prompt",
            ],
        }

    def _clean_prompt(self, prompt):
        prompt = str(prompt or "").replace("\n", " ").strip()
        for term in self.INTERNAL_TERMS:
            prompt = prompt.replace(term, "")
        return " ".join(prompt.split())

    def _deduplicate_phrases(self, prompt):
        phrases = [phrase.strip(" ,.") for phrase in prompt.split(",")]
        unique = []
        for phrase in phrases:
            if phrase and phrase not in unique:
                unique.append(phrase)
        return ", ".join(unique)

    def _limit_words(self, prompt, min_words, max_words):
        words = prompt.split()
        if len(words) > max_words:
            return " ".join(words[:max_words]).rstrip(" ,.")
        return prompt

    def _with_optimized_note(self, notes, state):
        notes = list(notes or [])
        if state.get("optimized_prompt") and "used optimized prompt" not in notes:
            notes.append("used optimized prompt")
        return notes

    def _with_conditioning_note(self, notes, conditioning, provider):
        notes = list(notes or [])
        if conditioning and conditioning.get("enabled"):
            supported = self._supports_conditioning(provider, conditioning)
            if not supported:
                notes.append("reference conditioning not supported by current provider")
            else:
                notes.append("reference conditioning package preserved for provider")
        return notes

    def _supports_conditioning(self, provider, conditioning):
        provider = str(provider or "").lower()
        conditioning_type = str(conditioning.get("conditioning_type") or "").lower()
        if provider in {"sdxl", "sdxl_quality"} and conditioning_type in {
            "img2img",
            "ip_adapter",
            "ip_adapter_planned",
            "controlnet",
        }:
            return True
        return False

    def _compile_flux_from_context(self, context_program, fallback_prompt):
        scene = context_program.get("scene") or {}
        characters = context_program.get("characters") or {}
        style = context_program.get("style") or {}
        layout = context_program.get("layout") or {}
        pose = context_program.get("pose") or {}
        expression = context_program.get("expression") or {}
        lighting = context_program.get("lighting") or {}
        quality = context_program.get("quality") or {}

        parts = [
            scene.get("narrative"),
            self._character_phrase(characters),
            ", ".join(style.get("style_keywords", [])[:6]),
            ", ".join(style.get("rendering_rules", [])[:4]),
            self._layout_phrase(layout),
            ", ".join(pose.get("pose_rules", [])[:4]),
            ", ".join(expression.get("expression_rules", [])[:4]),
            ", ".join(lighting.get("lighting_keywords", [])[:5]),
            ", ".join(quality.get("quality_keywords", [])[:4]),
        ]
        prompt = ", ".join(part for part in parts if part)
        return self._clean_prompt(prompt or fallback_prompt)

    def _compile_gpt_image_from_context(self, context_program, fallback_prompt):
        user_goal = context_program.get("user_goal") or {}
        lines = [
            "Create an image from this structured visual brief.",
            f"Goal: {user_goal.get('interpreted_goal') or fallback_prompt}",
            f"Subject: {self._character_phrase(context_program.get('characters') or {})}",
            f"Scene: {(context_program.get('scene') or {}).get('narrative') or ''}",
            f"Layout: {self._layout_phrase(context_program.get('layout') or {})}",
            f"Style: {', '.join((context_program.get('style') or {}).get('style_keywords', [])[:6])}",
            f"Lighting: {', '.join((context_program.get('lighting') or {}).get('lighting_keywords', [])[:5])}",
        ]
        return self._clean_prompt(" ".join(line for line in lines if line.strip()))

    def _negative_from_context(self, context_program, fallback_negative):
        negative = context_program.get("negative") or {}
        values = negative.get("negative_prompt", []) + negative.get("strict_avoid", [])
        return ", ".join(values) or fallback_negative or ""

    def _character_phrase(self, characters):
        count = characters.get("character_count") or 1
        rules = characters.get("preservation_rules") or []
        character_items = characters.get("characters") or []
        hints = [
            item.get("caption_hint")
            for item in character_items
            if isinstance(item, dict) and item.get("caption_hint")
        ]
        bits = [f"{count} recognizable character"]
        bits.extend(hints[:3])
        bits.extend(rules[:2])
        return ", ".join(str(bit) for bit in bits if bit)

    def _layout_phrase(self, layout):
        values = [
            layout.get("layout_type"),
            layout.get("aspect_ratio"),
            layout.get("frame_structure"),
            layout.get("camera_view"),
            layout.get("subject_placement"),
            ", ".join(layout.get("composition_rules", [])[:4]),
        ]
        return ", ".join(str(value) for value in values if value)
