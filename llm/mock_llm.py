from llm.base_llm import BaseLLM


class MockLLM(BaseLLM):
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

    def reason(self, state: dict) -> dict:
        user_prompt = str(state.get("user_prompt") or "").strip()
        caption = str(state.get("caption") or "").strip()
        text = f"{caption} {user_prompt}".strip()
        lower_text = text.lower()
        return {
            "user_goal": self._user_goal(user_prompt, caption),
            "scene_goal": self._scene_goal(lower_text),
            "composition_goal": self._composition_goal(lower_text),
            "interaction_goal": self._interaction_goal(lower_text),
            "style_goal": self._style_goal(lower_text),
            "priority": self._priority(lower_text),
            "mode": "mock_llm_rule_based",
        }

    def critic(self, state: dict, mode: str = "mock") -> dict:
        if mode == "disabled":
            return self._disabled_critic(state)
        if mode == "llm":
            report = self._disabled_critic(state)
            report["mode"] = "llm"
            report["reasoning_summary"] = (
                "Future LLM mode requested, but external LLM API calls are disabled."
            )
            report["used_fallback"] = True
            return report
        return self._mock_critic(state)

    def optimize(self, state: dict, mode: str = "mock") -> dict:
        prompt = state.get("canonical_prompt") or state.get("final_prompt") or ""
        provider = state.get("provider") or self._provider_from_routing(state)
        if mode == "disabled":
            return self._disabled_optimizer(prompt)
        if mode == "llm":
            return self._future_optimizer(prompt)
        return self._mock_optimizer(prompt, state, provider)

    def _user_goal(self, user_prompt, caption):
        if user_prompt and caption:
            return f"Transform the image subject into: {user_prompt}"
        if user_prompt:
            return f"Generate an image matching: {user_prompt}"
        if caption:
            return f"Generate an image based on: {caption}"
        return "Generate a clear image from the available context"

    def _scene_goal(self, text):
        if "photobooth" in text:
            return "create a photobooth memory scene"
        if "portrait" in text:
            return "create a focused character portrait"
        if "cinematic" in text:
            return "create a cinematic visual scene"
        if "group" in text or "friends" in text or "couple" in text:
            return "show relationship and shared moment clearly"
        return "create a coherent visual scene"

    def _composition_goal(self, text):
        if "photobooth" in text:
            return "use connected vertical frames with consistent camera distance"
        if "poster" in text:
            return "use strong center hierarchy and clean negative space"
        if "close" in text or "portrait" in text:
            return "use close or medium framing focused on the subject"
        return "use balanced composition with readable subject placement"

    def _interaction_goal(self, text):
        if "friends" in text:
            return "show friendly interaction and warm emotional connection"
        if "couple" in text:
            return "show gentle romantic connection without clutter"
        if "group" in text:
            return "keep each person visually separated and recognizable"
        return "keep the main subject expression and pose easy to read"

    def _style_goal(self, text):
        if "anime" in text:
            return "prioritize anime style with clean line art"
        if "webtoon" in text:
            return "prioritize soft webtoon rendering"
        if "realistic" in text:
            return "prioritize realistic lighting and texture"
        if "cinematic" in text:
            return "prioritize cinematic mood and lighting"
        return "prioritize high quality, coherent visual style"

    def _priority(self, text):
        priority = []
        if any(word in text for word in ("girl", "boy", "character", "person", "friends", "couple")):
            priority.append("character")
        if any(word in text for word in ("emotion", "smile", "warm", "cute", "romantic")):
            priority.append("emotion")
        if any(word in text for word in ("photobooth", "poster", "portrait", "layout", "frame")):
            priority.append("layout")
        if any(word in text for word in ("anime", "webtoon", "cinematic", "realistic", "style")):
            priority.append("style")
        for fallback in ("character", "emotion", "layout", "style"):
            if fallback not in priority:
                priority.append(fallback)
        return priority[:4]

    def _disabled_critic(self, state):
        score = int(state.get("prompt_quality_score") or 100)
        prompt_report = state.get("prompt_report") or {}
        suggestions = list(prompt_report.get("suggestions") or [])
        if not suggestions:
            suggestions.append("LLM prompt critic disabled; keep rule-based critic result")
        return {
            "mode": "disabled",
            "critic_score": score,
            "semantic_issues": [],
            "conflicts": [],
            "priority_issues": [],
            "provider_suitability_issues": [],
            "suggestions": suggestions,
            "priority_fix": [],
            "reasoning_summary": "Disabled mode used rule-based prompt report as baseline.",
            "used_fallback": True,
        }

    def _mock_critic(self, state):
        prompt = str(state.get("canonical_prompt") or state.get("final_prompt") or "")
        prompt_lower = prompt.lower()
        user_prompt = str(state.get("user_prompt") or "").lower()
        provider = str(state.get("provider") or "flux").lower()
        context_validation = state.get("context_validation") or {}
        prompt_quality_score = int(state.get("prompt_quality_score") or 100)
        context_program = state.get("context_program") or {}
        scene_plan = state.get("scene_plan") or {}

        semantic_issues = []
        conflicts = []
        priority_issues = []
        provider_suitability_issues = []
        suggestions = []
        priority_fix = []

        if "photobooth" in user_prompt and self._contains_any(prompt_lower, ("battle", "action", "combat")):
            conflicts.append("photobooth intent conflicts with battle/action/combat tone")
            suggestions.append("remove combat tone and preserve casual photobooth mood")
        if self._contains_any(user_prompt, ("soft", "warm")) and self._contains_any(prompt_lower, ("dramatic", "aggressive")):
            conflicts.append("soft/warm user intent conflicts with dramatic/aggressive prompt tone")
            suggestions.append("prioritize soft lighting and gentle mood")
        if int(context_validation.get("score") or 100) < 90:
            provider_suitability_issues.append("context validation score is below 90; provider prompt may inherit weak context")
            suggestions.append("fix context validation warnings before provider adaptation")
        if prompt_quality_score < 80:
            semantic_issues.append("rule-based prompt quality score is below 80")
            suggestions.append("repair missing or weak prompt sections before generation")
        if len(prompt.split()) > 120:
            provider_suitability_issues.append("prompt may be too long for FLUX")
            suggestions.append("compress prompt before provider adaptation")
        if provider == "flux" and self._looks_structured(prompt):
            provider_suitability_issues.append("FLUX prompt appears too structured; visual phrases may work better")
        if self._needs_character_preservation(state, context_program) and not self._contains_any(prompt_lower, ("preserve", "recognizable", "identity")):
            priority_issues.append("character preservation appears under-specified")
            priority_fix.append("add recognizable identity preservation before style details")

        layout_issue = self._scene_layout_issue(scene_plan, context_program)
        if layout_issue:
            semantic_issues.append(layout_issue)
            suggestions.append("align layout plan with scene goal")

        score = self._critic_score(prompt_quality_score, semantic_issues, conflicts, priority_issues, provider_suitability_issues)
        return {
            "mode": "mock",
            "critic_score": score,
            "semantic_issues": semantic_issues,
            "conflicts": conflicts,
            "priority_issues": priority_issues,
            "provider_suitability_issues": provider_suitability_issues,
            "suggestions": suggestions or ["prompt is semantically acceptable in mock critic"],
            "priority_fix": priority_fix,
            "reasoning_summary": self._critic_summary(semantic_issues, conflicts, priority_issues, provider_suitability_issues),
            "used_fallback": False,
        }

    def _disabled_optimizer(self, prompt):
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

    def _mock_optimizer(self, prompt, state, provider):
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

    def _future_optimizer(self, prompt):
        return {
            "llm_optimized_prompt": prompt,
            "canonical_prompt": prompt,
            "final_prompt": prompt,
            "llm_optimizer_report": {
                "mode": "llm",
                "reason": "Future LLM provider is configured; external API calls are disabled.",
                "changes": ["kept rule-based optimized prompt as fallback"],
                "used_fallback": True,
            },
        }

    def _contains_any(self, text, words):
        return any(word in text for word in words)

    def _looks_structured(self, prompt):
        return self._contains_any(prompt.lower(), ("task:", "scene:", "layout:", "style:", "{", "}", "context_program"))

    def _needs_character_preservation(self, state, context_program):
        user_prompt = str(state.get("user_prompt") or "").lower()
        characters = (context_program.get("characters") or {}).get("characters") or []
        return bool(characters) or self._contains_any(user_prompt, ("reference", "same character", "identity", "preserve"))

    def _scene_layout_issue(self, scene_plan, context_program):
        scene_text = " ".join(str(value).lower() for value in (scene_plan or {}).values())
        layout_type = str((context_program.get("layout") or {}).get("layout_type") or "").lower()
        if "photobooth" in scene_text and layout_type in {"poster", "cinematic"}:
            return "scene goal suggests photobooth but layout plan suggests poster/cinematic"
        if "portrait" in scene_text and layout_type in {"comic_page", "sticker_sheet"}:
            return "scene goal suggests portrait but layout plan suggests multi-panel layout"
        return ""

    def _critic_score(self, base_score, semantic_issues, conflicts, priority_issues, provider_suitability_issues):
        score = int(base_score)
        score -= len(semantic_issues) * 8
        score -= len(conflicts) * 12
        score -= len(priority_issues) * 7
        score -= len(provider_suitability_issues) * 5
        return max(0, min(100, score))

    def _critic_summary(self, semantic_issues, conflicts, priority_issues, provider_suitability_issues):
        total = len(semantic_issues) + len(conflicts) + len(priority_issues) + len(provider_suitability_issues)
        if total == 0:
            return "Mock LLM critic found no major semantic prompt issues."
        return f"Mock LLM critic found {total} semantic or provider suitability issue(s)."

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
        return (state.get("provider_routing") or {}).get("selected_provider", "flux")

    def _normalize_spaces(self, prompt):
        return " ".join(str(prompt or "").replace("\n", " ").split())
