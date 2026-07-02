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
            result = self._run_legacy(
                state.get("canonical_prompt") or state.get("final_prompt", ""),
                negative_prompt=state.get("negative_prompt"),
                provider=state.get("provider", "flux"),
                prompt_sections=state.get("prompt_sections"),
                scene_plan=state.get("scene_plan"),
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
                "adapter_notes": self._with_optimized_note(
                    result.get("adapter_notes", []),
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
    ) -> dict:
        print("[ProviderPromptAdapter] Running...")
        provider = (provider or "flux").lower()
        fallback_used = False
        if provider not in {"flux", "gpt_image", "sdxl"}:
            provider = "flux"
            fallback_used = True
        print(f"[ProviderPromptAdapter] Provider: {provider}")

        if provider == "gpt_image":
            result = self._adapt_gpt_image(canonical_prompt, negative_prompt, prompt_sections)
            if fallback_used:
                result["adapter_notes"].append("unknown provider fallback to flux")
            return result
        if provider == "sdxl":
            result = self._adapt_sdxl(canonical_prompt, negative_prompt)
            if fallback_used:
                result["adapter_notes"].append("unknown provider fallback to flux")
            return result
        result = self._adapt_flux(canonical_prompt, negative_prompt, scene_plan)
        if fallback_used:
            result["adapter_notes"].append("unknown provider fallback to flux")
        return result

    def _adapt_flux(self, canonical_prompt, negative_prompt, scene_plan):
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
            ],
        }

    def _adapt_gpt_image(self, canonical_prompt, negative_prompt, prompt_sections):
        return {
            "provider": "gpt_image",
            "provider_prompt": (
                "Create an image using this structured instruction: "
                f"{self._clean_prompt(canonical_prompt)}"
            ),
            "provider_negative_prompt": negative_prompt or "",
            "adapter_notes": [
                "skeleton adapter for GPT Image",
                "structured instruction format",
            ],
            "sections": prompt_sections or {},
        }

    def _adapt_sdxl(self, canonical_prompt, negative_prompt):
        return {
            "provider": "sdxl",
            "provider_prompt": self._clean_prompt(canonical_prompt),
            "provider_negative_prompt": negative_prompt or "",
            "adapter_notes": [
                "skeleton adapter for SDXL",
                "separated prompt and negative prompt",
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
