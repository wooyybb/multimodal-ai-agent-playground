from llm.openai_reasoner import dumps_payload
from llm.reasoner_router import ReasonerRouter


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

    def __init__(self, reasoner_router=None):
        self.reasoner_router = reasoner_router or ReasonerRouter()

    def run(self, state: dict) -> dict:
        print("[PromptOptimizer] Running...")
        print("[PromptOptimizer] Reading prompt report...")
        state = state or {}
        original_prompt = state.get("canonical_prompt") or state.get("final_prompt") or ""
        prompt_report = state.get("prompt_report") or {}
        quality_score = state.get("prompt_quality_score")
        if quality_score is None:
            quality_score = prompt_report.get("quality_score", 100)
        quality_score = int(quality_score or 100)

        print("[PromptOptimizer] Reasoning...")
        reasoning_steps = []
        warnings = self._warnings(prompt_report)
        duplicate_keywords = prompt_report.get("duplicate_keywords") or []

        length_before = self._word_count(original_prompt)
        actions = []

        prompt, keywords_removed = self._remove_internal_terms(original_prompt)
        if keywords_removed:
            actions.append("removed internal/debug terms")
            reasoning_steps.append("Removed internal workflow context")

        prompt, duplicates_removed = self._remove_reported_duplicates(
            prompt,
            duplicate_keywords,
        )
        if duplicates_removed:
            actions.append("removed duplicate phrases")
            reasoning_steps.append("Removed duplicated keyword")

        print("[PromptOptimizer] Applying optimization...")
        prompt, keywords_added, missing_reasoning = self._repair_missing_sections(
            prompt,
            prompt_report,
        )
        reasoning_steps.extend(missing_reasoning)
        if keywords_added:
            actions.append("added missing section repair keywords")

        if self._has_warning(warnings, "prompt is too short"):
            prompt, short_keywords = self._append_missing_keywords(
                prompt,
                ["high quality", "clean details"],
            )
            keywords_added.extend(short_keywords)
            if short_keywords:
                actions.append("added short-prompt quality tags")
                reasoning_steps.append("Prompt was too short; added quality tags")

        if quality_score < 70:
            prompt, quality_keywords = self._append_missing_keywords(
                prompt,
                self.QUALITY_KEYWORDS,
            )
            keywords_added.extend(quality_keywords)
            if quality_keywords:
                actions.append("added low-score quality hints")
                reasoning_steps.append("Quality score below 70; added quality keywords")
        elif quality_score >= 90 and not keywords_added and not duplicates_removed:
            reasoning_steps.append("Quality score is high; kept prompt mostly unchanged")
        elif 70 <= quality_score < 90:
            reasoning_steps.append("Quality score is medium; applied targeted repairs only")

        should_compress = (
            self._has_warning(warnings, "prompt is too long")
            or self._word_count(prompt) > 120
        )
        prompt, trimmed = self._limit_words(prompt, max_words=100 if should_compress else 120)
        if trimmed:
            actions.append("trimmed prompt to length budget")
            reasoning_steps.append("Prompt compressed")
        else:
            reasoning_steps.append("Lighting preserved")

        optimized_prompt = prompt.strip(" ,.")
        length_after = self._word_count(optimized_prompt)
        after_estimated_score = self._estimate_score(
            quality_score,
            duplicates_removed,
            keywords_added,
            trimmed,
        )

        print(f"[PromptOptimizer] Length before: {length_before}")
        print(f"[PromptOptimizer] Length after: {length_after}")
        print(f"[PromptOptimizer] Removed duplicates: {duplicates_removed}")
        print(f"[PromptOptimizer] Added keywords: {keywords_added}")
        print(f"[PromptOptimizer] Removed: {duplicates_removed + keywords_removed}")
        print(f"[PromptOptimizer] Added: {keywords_added}")
        print(f"[PromptOptimizer] Compressed: {trimmed}")
        print(
            "[PromptOptimizer] Estimated Improvement: "
            f"{quality_score} -> {after_estimated_score}"
        )
        print("[PromptOptimizer] Optimization finished.")

        fallback_result = {
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
                "reasoning_steps": reasoning_steps,
                "before_score": quality_score,
                "after_estimated_score": after_estimated_score,
            },
        }
        return self._apply_reasoning(state, fallback_result)

    def _apply_reasoning(self, state, fallback_result):
        system_prompt = (
            "You are a prompt optimizer. Return only JSON with keys: "
            "optimized_prompt and optimization_report. "
            "optimization_report must include reasoning_steps, actions, before_score, "
            "after_estimated_score, keywords_added, keywords_removed."
        )
        user_prompt = dumps_payload(
            {
                "task": "prompt_optimizer",
                "canonical_prompt": state.get("canonical_prompt") or state.get("final_prompt"),
                "prompt_report": state.get("prompt_report"),
                "prompt_quality_score": state.get("prompt_quality_score"),
                "scene_plan": state.get("scene_plan"),
                "fallback_result": fallback_result,
            }
        )
        result = self.reasoner_router.reason(
            system_prompt,
            user_prompt,
            fallback=fallback_result,
            schema_name="optimization_report",
        )
        optimized_prompt = result.get("optimized_prompt") or fallback_result["optimized_prompt"]
        optimization_report = result.get("optimization_report")
        if not isinstance(optimization_report, dict):
            optimization_report = fallback_result["optimization_report"]
        optimization_report = dict(optimization_report)
        optimization_report["reasoning_provider"] = result.get("reasoning_provider")
        optimization_report["reasoning_used_fallback"] = result.get("reasoning_used_fallback")
        optimization_report["reasoning_latency"] = result.get("reasoning_latency")
        if result.get("reasoning_fallback_reason"):
            optimization_report["reasoning_fallback_reason"] = result.get(
                "reasoning_fallback_reason"
            )
        return {
            "optimized_prompt": optimized_prompt,
            "canonical_prompt": optimized_prompt,
            "final_prompt": optimized_prompt,
            "optimization_report": optimization_report,
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

    def _remove_reported_duplicates(self, prompt, duplicate_keywords):
        if not duplicate_keywords:
            return prompt, []

        duplicate_terms = []
        for item in duplicate_keywords:
            if isinstance(item, dict):
                keyword = item.get("keyword")
            else:
                keyword = str(item)
            if keyword:
                duplicate_terms.append(str(keyword).lower())

        phrases = [phrase.strip(" ,.") for phrase in str(prompt or "").split(",")]
        unique = []
        duplicates_removed = []
        seen_phrases = set()
        seen_terms = set()
        for phrase in phrases:
            if not phrase:
                continue
            phrase_key = phrase.lower()
            matched_term = next(
                (term for term in duplicate_terms if term in phrase_key),
                None,
            )
            if matched_term and matched_term in seen_terms:
                duplicates_removed.append(phrase)
                continue
            if phrase_key in seen_phrases:
                duplicates_removed.append(phrase)
                continue
            if matched_term:
                seen_terms.add(matched_term)
            seen_phrases.add(phrase_key)
            unique.append(phrase)
        return ", ".join(unique), duplicates_removed

    def _repair_missing_sections(self, prompt, prompt_report):
        missing_sections = prompt_report.get("missing_sections") or []
        keywords = []
        reasoning_steps = []
        for section in missing_sections:
            section_key = str(section).lower().replace(" ", "_")
            for key, values in self.MISSING_SECTION_KEYWORDS.items():
                if key in section_key:
                    keywords.extend(values)
                    reasoning_steps.append(f"{key.title()} section added")
        prompt, additions = self._append_missing_keywords(prompt, keywords)
        return prompt, additions, reasoning_steps

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

    def _warnings(self, prompt_report):
        warnings = prompt_report.get("warnings")
        if warnings is None:
            warnings = prompt_report.get("warning", [])
        if isinstance(warnings, str):
            return [warnings]
        return list(warnings or [])

    def _has_warning(self, warnings, expected):
        expected = expected.lower()
        return any(expected in str(warning).lower() for warning in warnings)

    def _estimate_score(self, before_score, duplicates_removed, keywords_added, trimmed):
        score = before_score
        score += min(10, len(duplicates_removed) * 3)
        score += min(15, len(keywords_added) * 2)
        if trimmed:
            score += 5
        return max(0, min(100, score))
