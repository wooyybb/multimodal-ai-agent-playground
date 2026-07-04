class SelfVerificationAgent:
    def run(self, state: dict) -> dict:
        print("[SelfVerification] Running...")
        state = state or {}
        best_score = self._score(state)
        context_validation = state.get("context_validation") or {}
        prompt_report = state.get("prompt_report") or {}
        llm_report = state.get("llm_prompt_critic_report") or {}
        goal_tree = state.get("goal_tree") or {}
        character_program = state.get("character_program") or {}
        provider_prompt = str(
            state.get("provider_prompt")
            or state.get("final_prompt")
            or state.get("canonical_prompt")
            or ""
        )

        findings = []
        blocking_issues = []
        recommendations = []

        goal_score = self._goal_satisfaction_score(best_score, findings)
        prompt_score = self._prompt_consistency_score(prompt_report, findings)
        context_score = self._context_consistency_score(context_validation, findings)

        self._check_llm_conflicts(llm_report, blocking_issues, recommendations)
        self._check_identity_priority(
            goal_tree,
            provider_prompt,
            findings,
            blocking_issues,
            recommendations,
        )
        self._check_character_program(
            character_program,
            provider_prompt,
            findings,
            recommendations,
        )

        needs_replanning = (
            best_score < 0.65
            or bool(blocking_issues)
            or goal_score < 70
            or prompt_score < 70
            or context_score < 70
        )
        overall_pass = not needs_replanning and min(
            goal_score,
            prompt_score,
            context_score,
        ) >= 70

        if needs_replanning:
            recommendations.append("run strategy selection before adaptive planning")
        elif not recommendations:
            recommendations.append("current state is acceptable; prefer low-risk retry strategy")

        result = {
            "overall_pass": overall_pass,
            "goal_satisfaction_score": goal_score,
            "prompt_consistency_score": prompt_score,
            "context_consistency_score": context_score,
            "needs_replanning": needs_replanning,
            "verification_findings": findings,
            "blocking_issues": blocking_issues,
            "recommendations": list(dict.fromkeys(recommendations)),
        }

        print(f"[SelfVerification] Overall pass: {overall_pass}")
        print(f"[SelfVerification] Needs replanning: {needs_replanning}")
        return {"self_verification": result}

    def _score(self, state):
        value = state.get("best_score")
        if value is None:
            value = state.get("score")
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def _goal_satisfaction_score(self, best_score, findings):
        if best_score >= 0.70:
            findings.append("evaluation score suggests goal is mostly satisfied")
            return 85
        if best_score < 0.65:
            findings.append("evaluation score is below replanning threshold")
            return 55
        findings.append("evaluation score is marginal")
        return 70

    def _prompt_consistency_score(self, prompt_report, findings):
        score = 90
        missing = prompt_report.get("missing_sections") or []
        if missing:
            score -= min(40, len(missing) * 10)
            findings.append(f"prompt is missing sections: {missing}")
        duplicates = prompt_report.get("duplicate_keywords") or []
        if duplicates:
            score -= min(15, len(duplicates) * 3)
            findings.append("prompt has duplicate keywords")
        return max(0, min(100, score))

    def _context_consistency_score(self, context_validation, findings):
        score = int(context_validation.get("score", 100) or 100)
        if score < 90:
            findings.append("context validation score is below 90")
        if context_validation.get("missing_keys"):
            findings.append("context program has missing keys")
        return max(0, min(100, score))

    def _check_llm_conflicts(self, llm_report, blocking_issues, recommendations):
        conflicts = llm_report.get("conflicts") or []
        if conflicts:
            blocking_issues.append(f"semantic conflicts detected: {conflicts}")
            recommendations.append("resolve semantic conflicts before adaptive retry")

    def _check_identity_priority(
        self,
        goal_tree,
        provider_prompt,
        findings,
        blocking_issues,
        recommendations,
    ):
        priorities = goal_tree.get("priorities") or {}
        identity_priority = float(priorities.get("identity") or 0.0)
        prompt_text = provider_prompt.lower()
        identity_terms = ("identity", "preserve", "recognizable", "character")
        if identity_priority >= 0.9 and not any(term in prompt_text for term in identity_terms):
            issue = "identity priority is high but provider prompt lacks preservation language"
            findings.append(issue)
            blocking_issues.append(issue)
            recommendations.append("increase identity preservation strategy")

    def _check_character_program(
        self,
        character_program,
        provider_prompt,
        findings,
        recommendations,
    ):
        if not character_program:
            return
        prompt_text = provider_prompt.lower()
        appearance = character_program.get("appearance") or {}
        accessories = appearance.get("accessories") or []
        outfit = str(appearance.get("outfit") or "")
        missing_details = []
        if outfit and outfit.lower() not in prompt_text:
            missing_details.append(outfit)
        for item in accessories[:3]:
            if str(item).lower() not in prompt_text:
                missing_details.append(str(item))
        if missing_details:
            findings.append(
                "provider prompt may not preserve character details: "
                + ", ".join(missing_details)
            )
            recommendations.append("include character program details in retry strategy")
