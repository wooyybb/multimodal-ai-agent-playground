class PromptOptimizerAgent:
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
    MISSING_SECTION_KEYWORDS = {
        "layout": ["balanced composition", "clear framing"],
        "style": ["clean visual style"],
        "lighting": ["soft lighting"],
        "character": ["clear recognizable subject"],
        "expression": ["natural readable expression"],
        "pose": ["relaxed natural pose"],
    }
    QUALITY_KEYWORDS = ["clear composition", "readable silhouette", "clean details"]

    def run(self, state: dict) -> dict:
        print("[PromptOptimizer] Running...")
        state = state or {}
        original_prompt = state.get("canonical_prompt") or state.get("final_prompt") or ""
        prompt_report = state.get("prompt_report") or {}
        quality_score = state.get("prompt_quality_score")
        if quality_score is None:
            quality_score = prompt_report.get("quality_score", 100)

        length_before = self._word_count(original_prompt)
        actions = []

        prompt, keywords_removed = self._remove_internal_terms(original_prompt)
        if keywords_removed:
            actions.append("removed internal/debug terms")

        prompt, duplicates_removed = self._deduplicate_phrases(prompt)
        if duplicates_removed:
            actions.append("removed duplicate phrases")

        prompt, keywords_added = self._repair_missing_sections(prompt, prompt_report)
        if keywords_added:
            actions.append("added missing section repair keywords")

        if quality_score < 70:
            prompt, quality_keywords = self._append_missing_keywords(
                prompt,
                self.QUALITY_KEYWORDS,
            )
            keywords_added.extend(quality_keywords)
            if quality_keywords:
                actions.append("added low-score quality hints")

        prompt, trimmed = self._limit_words(prompt, max_words=100)
        if trimmed:
            actions.append("trimmed prompt to length budget")

        optimized_prompt = prompt.strip(" ,.")
        length_after = self._word_count(optimized_prompt)

        print(f"[PromptOptimizer] Length before: {length_before}")
        print(f"[PromptOptimizer] Length after: {length_after}")
        print(f"[PromptOptimizer] Removed duplicates: {duplicates_removed}")
        print(f"[PromptOptimizer] Added keywords: {keywords_added}")

        return {
            "optimized_prompt": optimized_prompt,
            "canonical_prompt": optimized_prompt,
            "final_prompt": optimized_prompt,
            "optimization_report": {
                "length_before": length_before,
                "length_after": length_after,
                "duplicates_removed": duplicates_removed,
                "keywords_added": keywords_added,
                "keywords_removed": keywords_removed,
                "actions": actions,
            },
        }

    def _remove_internal_terms(self, prompt):
        cleaned = str(prompt or "")
        removed = []
        lowered = cleaned.lower()
        for term in self.INTERNAL_TERMS:
            if term in lowered:
                removed.append(term)
                cleaned = cleaned.replace(term, "")
                cleaned = cleaned.replace(term.title(), "")
                cleaned = cleaned.replace(term.upper(), "")
                lowered = cleaned.lower()
        return self._normalize_spaces(cleaned), removed

    def _deduplicate_phrases(self, prompt):
        phrases = [phrase.strip(" ,.") for phrase in str(prompt or "").split(",")]
        unique = []
        seen = set()
        duplicates_removed = []
        for phrase in phrases:
            if not phrase:
                continue
            key = phrase.lower()
            if key in seen:
                duplicates_removed.append(phrase)
                continue
            seen.add(key)
            unique.append(phrase)
        return ", ".join(unique), duplicates_removed

    def _repair_missing_sections(self, prompt, prompt_report):
        missing_sections = prompt_report.get("missing_sections") or []
        keywords = []
        for section in missing_sections:
            section_key = str(section).lower().replace(" ", "_")
            for key, values in self.MISSING_SECTION_KEYWORDS.items():
                if key in section_key:
                    keywords.extend(values)
        return self._append_missing_keywords(prompt, keywords)

    def _append_missing_keywords(self, prompt, keywords):
        additions = []
        prompt_text = str(prompt or "")
        lowered = prompt_text.lower()
        for keyword in keywords:
            if keyword.lower() not in lowered:
                additions.append(keyword)
                lowered += f" {keyword.lower()}"
        if additions:
            prompt_text = f"{prompt_text}, {', '.join(additions)}"
        return prompt_text, additions

    def _limit_words(self, prompt, max_words):
        phrases = [phrase.strip(" ,.") for phrase in str(prompt or "").split(",")]
        kept = []
        total_words = 0
        trimmed = False

        preservation_phrases = [
            phrase for phrase in phrases if "recognizable" in phrase.lower()
        ]
        for phrase in preservation_phrases:
            words = phrase.split()
            if total_words + len(words) <= max_words and phrase not in kept:
                kept.append(phrase)
                total_words += len(words)

        for phrase in phrases:
            if not phrase or phrase in kept:
                continue
            words = phrase.split()
            if total_words + len(words) > max_words:
                trimmed = True
                continue
            kept.append(phrase)
            total_words += len(words)

        return ", ".join(kept), trimmed

    def _word_count(self, prompt):
        return len(str(prompt or "").replace("\n", " ").split())

    def _normalize_spaces(self, prompt):
        return " ".join(str(prompt or "").replace("\n", " ").split())
