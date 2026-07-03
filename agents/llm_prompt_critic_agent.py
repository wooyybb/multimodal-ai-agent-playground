import os


class LLMPromptCriticAgent:
    def run(self, state: dict) -> dict:
        print("[LLMPromptCritic] Running...")
        state = state or {}
        mode = self._mode()

        try:
            if mode == "mock":
                report = self._run_mock_critic(state)
            elif mode == "llm":
                report = self._run_llm_critic(state)
            else:
                report = self._run_disabled_critic(state)
        except Exception as error:
            print(f"[LLMPromptCritic] Error: {error}")
            report = self._fallback_report(state, reason=str(error))

        print(f"[LLMPromptCritic] Mode: {report['mode']}")
        print(f"[LLMPromptCritic] Critic score: {report['critic_score']}")
        print(f"[LLMPromptCritic] Conflicts: {report['conflicts']}")
        print(f"[LLMPromptCritic] Suggestions: {report['suggestions']}")
        return {
            "llm_prompt_critic_report": report,
            "llm_prompt_critic_score": report["critic_score"],
        }

    def _mode(self):
        enabled = os.getenv("LLM_PROMPT_CRITIC_ENABLED", "").lower() == "true"
        mock = os.getenv("LLM_PROMPT_CRITIC_MOCK", "").lower() == "true"
        if not enabled:
            return "disabled"
        if mock:
            return "mock"
        return "llm"

    def _run_disabled_critic(self, state):
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

    def _run_mock_critic(self, state):
        prompt = self._prompt(state)
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

        if "photobooth" in user_prompt and self._contains_any(
            prompt_lower,
            ("battle", "action", "combat"),
        ):
            conflicts.append("photobooth intent conflicts with battle/action/combat tone")
            suggestions.append("remove combat tone and preserve casual photobooth mood")

        if self._contains_any(user_prompt, ("soft", "warm")) and self._contains_any(
            prompt_lower,
            ("dramatic", "aggressive"),
        ):
            conflicts.append("soft/warm user intent conflicts with dramatic/aggressive prompt tone")
            suggestions.append("prioritize soft lighting and gentle mood")

        if int(context_validation.get("score") or 100) < 90:
            provider_suitability_issues.append(
                "context validation score is below 90; provider prompt may inherit weak context"
            )
            suggestions.append("fix context validation warnings before provider adaptation")

        if prompt_quality_score < 80:
            semantic_issues.append("rule-based prompt quality score is below 80")
            suggestions.append("repair missing or weak prompt sections before generation")

        word_count = len(prompt.split())
        if word_count > 120:
            provider_suitability_issues.append("prompt may be too long for FLUX")
            suggestions.append("compress prompt before provider adaptation")

        if provider == "flux" and self._looks_structured(prompt):
            provider_suitability_issues.append(
                "FLUX prompt appears too structured; visual phrases may work better"
            )

        if self._needs_character_preservation(state, context_program) and not self._contains_any(
            prompt_lower,
            ("preserve", "recognizable", "identity"),
        ):
            priority_issues.append("character preservation appears under-specified")
            priority_fix.append("add recognizable identity preservation before style details")

        layout_issue = self._scene_layout_issue(scene_plan, context_program)
        if layout_issue:
            semantic_issues.append(layout_issue)
            suggestions.append("align layout plan with scene goal")

        score = self._score(
            prompt_quality_score,
            semantic_issues,
            conflicts,
            priority_issues,
            provider_suitability_issues,
        )
        return {
            "mode": "mock",
            "critic_score": score,
            "semantic_issues": semantic_issues,
            "conflicts": conflicts,
            "priority_issues": priority_issues,
            "provider_suitability_issues": provider_suitability_issues,
            "suggestions": suggestions or ["prompt is semantically acceptable in mock critic"],
            "priority_fix": priority_fix,
            "reasoning_summary": self._summary(
                semantic_issues,
                conflicts,
                priority_issues,
                provider_suitability_issues,
            ),
            "used_fallback": False,
        }

    def _run_llm_critic(self, state):
        fallback = self._fallback_report(
            state,
            reason="Future LLM mode requested, but external LLM API calls are disabled.",
        )
        fallback["mode"] = "llm"
        return fallback

    def _fallback_report(self, state, reason):
        report = self._run_disabled_critic(state)
        report["reasoning_summary"] = reason
        report["used_fallback"] = True
        return report

    def _prompt(self, state):
        return str(state.get("canonical_prompt") or state.get("final_prompt") or "")

    def _contains_any(self, text, words):
        return any(word in text for word in words)

    def _looks_structured(self, prompt):
        markers = ("task:", "scene:", "layout:", "style:", "{", "}", "context_program")
        return self._contains_any(prompt.lower(), markers)

    def _needs_character_preservation(self, state, context_program):
        user_prompt = str(state.get("user_prompt") or "").lower()
        characters = (context_program.get("characters") or {}).get("characters") or []
        return bool(characters) or self._contains_any(
            user_prompt,
            ("reference", "same character", "identity", "preserve"),
        )

    def _scene_layout_issue(self, scene_plan, context_program):
        scene_text = " ".join(str(value).lower() for value in (scene_plan or {}).values())
        layout = context_program.get("layout") or {}
        layout_type = str(layout.get("layout_type") or "").lower()
        if "photobooth" in scene_text and layout_type in {"poster", "cinematic"}:
            return "scene goal suggests photobooth but layout plan suggests poster/cinematic"
        if "portrait" in scene_text and layout_type in {"comic_page", "sticker_sheet"}:
            return "scene goal suggests portrait but layout plan suggests multi-panel layout"
        return ""

    def _score(
        self,
        base_score,
        semantic_issues,
        conflicts,
        priority_issues,
        provider_suitability_issues,
    ):
        score = int(base_score)
        score -= len(semantic_issues) * 8
        score -= len(conflicts) * 12
        score -= len(priority_issues) * 7
        score -= len(provider_suitability_issues) * 5
        return max(0, min(100, score))

    def _summary(
        self,
        semantic_issues,
        conflicts,
        priority_issues,
        provider_suitability_issues,
    ):
        total = (
            len(semantic_issues)
            + len(conflicts)
            + len(priority_issues)
            + len(provider_suitability_issues)
        )
        if total == 0:
            return "Mock LLM critic found no major semantic prompt issues."
        return f"Mock LLM critic found {total} semantic or provider suitability issue(s)."
