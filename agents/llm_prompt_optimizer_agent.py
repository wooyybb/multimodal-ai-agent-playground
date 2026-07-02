import os


class LLMPromptOptimizerAgent:
    INTERNAL_TERMS = (
        "image_generation",
        "full workflow",
        "previous attempt needs improvement",
        "memory hint",
        "planner hint",
        "similar previous run found",
        "agent trace",
        "prompt quality score",
        "internal context",
    )
    GENERIC_TAGS = (
        "masterpiece",
        "best quality",
        "ultra detailed",
        "trending on artstation",
    )

    def run(self, state: dict) -> dict:
        print("[LLMPromptOptimizer] Running...")
        state = state or {}
        prompt = state.get("canonical_prompt") or state.get("final_prompt") or ""
        provider = state.get("provider") or self._provider_from_routing(state)
        mode = self._mode()

        print(f"[LLMPromptOptimizer] Mode: {mode}")
        if mode == "mock":
            result = self._run_mock_optimizer(prompt, state, provider)
        elif mode == "llm":
            result = self._run_llm_optimizer(prompt, state, provider)
        else:
            result = self._disabled(prompt)

        print(f"[LLMPromptOptimizer] Used fallback: {result['llm_optimizer_report']['used_fallback']}")
        return result

    def _mode(self):
        if os.getenv("LLM_OPTIMIZER_MOCK", "").lower() == "true":
            return "mock"
        if os.getenv("LLM_OPTIMIZER_ENABLED", "").lower() == "true":
            return "llm"
        return "disabled"

    def _disabled(self, prompt):
        return {
            "llm_optimized_prompt": prompt,
            "canonical_prompt": prompt,
            "final_prompt": prompt,
            "llm_optimizer_report": {
                "mode": "disabled",
                "reason": "LLM optimizer is disabled; using existing optimized prompt.",
                "changes": [],
                "used_fallback": True,
            },
        }

    def _run_mock_optimizer(self, prompt, state, provider):
        changes = []
        optimized = self._remove_internal_terms(prompt, changes)
        optimized = self._trim_generic_tags(optimized, changes)
        optimized = self._deduplicate_phrases(optimized, changes)
        optimized = self._preserve_core_sections(optimized, state, changes)
        optimized = self._fit_provider_density(optimized, provider, changes)

        return {
            "llm_optimized_prompt": optimized,
            "canonical_prompt": optimized,
            "final_prompt": optimized,
            "llm_optimizer_report": {
                "mode": "mock",
                "reason": "Mock LLM optimizer ran without external API calls.",
                "changes": changes,
                "used_fallback": False,
            },
        }

    def _run_llm_optimizer(self, prompt, state, provider):
        provider_name = os.getenv("LLM_OPTIMIZER_PROVIDER", "openai")
        return {
            "llm_optimized_prompt": prompt,
            "canonical_prompt": prompt,
            "final_prompt": prompt,
            "llm_optimizer_report": {
                "mode": "llm",
                "reason": (
                    f"LLM provider '{provider_name}' is configured as a future "
                    "integration point; external API calls are disabled in this Sprint."
                ),
                "changes": ["kept rule-based optimized prompt as fallback"],
                "used_fallback": True,
            },
        }

    def _remove_internal_terms(self, prompt, changes):
        optimized = str(prompt or "")
        lowered = optimized.lower()
        removed = []
        for term in self.INTERNAL_TERMS:
            if term in lowered:
                removed.append(term)
                optimized = optimized.replace(term, "")
                optimized = optimized.replace(term.title(), "")
                optimized = optimized.replace(term.upper(), "")
                lowered = optimized.lower()
        if removed:
            changes.append(f"removed internal terms: {', '.join(removed)}")
        return self._normalize_spaces(optimized)

    def _trim_generic_tags(self, prompt, changes):
        phrases = [phrase.strip(" ,.") for phrase in str(prompt or "").split(",")]
        kept = []
        removed = []
        seen_generic = set()
        for phrase in phrases:
            key = phrase.lower()
            generic = next((tag for tag in self.GENERIC_TAGS if tag in key), None)
            if generic and generic in seen_generic:
                removed.append(phrase)
                continue
            if generic:
                seen_generic.add(generic)
            if phrase:
                kept.append(phrase)
        if removed:
            changes.append(f"trimmed repeated generic tags: {', '.join(removed)}")
        return ", ".join(kept)

    def _deduplicate_phrases(self, prompt, changes):
        phrases = [phrase.strip(" ,.") for phrase in str(prompt or "").split(",")]
        kept = []
        removed = []
        seen = set()
        for phrase in phrases:
            key = phrase.lower()
            if not phrase:
                continue
            if key in seen:
                removed.append(phrase)
                continue
            seen.add(key)
            kept.append(phrase)
        if removed:
            changes.append(f"deduplicated phrases: {', '.join(removed)}")
        return ", ".join(kept)

    def _preserve_core_sections(self, prompt, state, changes):
        additions = []
        sections = state.get("prompt_sections") or {}
        for section_name in ("character", "layout", "style"):
            if sections.get(section_name) and section_name not in prompt.lower():
                additions.append(f"preserve {section_name} intent")
        if additions:
            changes.append("preserved core character/layout/style intent")
            return f"{prompt}, {', '.join(additions)}"
        return prompt

    def _fit_provider_density(self, prompt, provider, changes):
        max_words = 95 if provider == "flux" else 130
        words = str(prompt or "").split()
        if len(words) <= max_words:
            changes.append(f"kept provider density for {provider or 'default provider'}")
            return prompt
        changes.append(f"trimmed prompt density for {provider}")
        return " ".join(words[:max_words]).rstrip(" ,.")

    def _provider_from_routing(self, state):
        routing = state.get("provider_routing") or {}
        return routing.get("selected_provider", "flux")

    def _normalize_spaces(self, prompt):
        return " ".join(str(prompt or "").replace("\n", " ").split())
