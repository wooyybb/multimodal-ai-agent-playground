from llm.openai_reasoner import dumps_payload
from llm.reasoner_router import ReasonerRouter


class PromptCriticAgent:
    REQUIRED_SECTIONS = {
        "Character": ("character", "character_section"),
        "Style": ("style", "style_section"),
        "Layout": ("layout", "layout_section"),
        "Pose": ("pose", "pose_section"),
        "Expression": ("expression", "expression_section"),
        "Lighting": ("lighting", "lighting_section"),
        "Negative Prompt": ("negative", "negative_prompt", "negative_section"),
    }
    DUPLICATE_KEYWORDS = (
        "masterpiece",
        "high quality",
        "cinematic lighting",
        "anime style",
    )

    def __init__(self, reasoner_router=None):
        self.reasoner_router = reasoner_router or ReasonerRouter()

    def run(
        self,
        state_or_canonical_prompt,
        prompt_sections=None,
        scene_plan=None,
    ):
        if isinstance(state_or_canonical_prompt, dict):
            state = state_or_canonical_prompt
            report = self._run_legacy(
                state.get("canonical_prompt") or state.get("final_prompt", ""),
                prompt_sections=state.get("prompt_sections", {}),
                scene_plan=state.get("scene_plan"),
            )
            report = self._apply_reasoning(state, report)
            return {
                "prompt_report": report,
                "prompt_quality_score": report.get("quality_score", 100),
            }

        return self._run_legacy(
            state_or_canonical_prompt,
            prompt_sections=prompt_sections,
            scene_plan=scene_plan,
        )

    def _run_legacy(
        self,
        canonical_prompt,
        prompt_sections=None,
        scene_plan=None,
    ):
        print("[PromptCritic] Running...")
        prompt = str(canonical_prompt or "")
        prompt_sections = prompt_sections or {}

        duplicate_keywords = self._find_duplicate_keywords(prompt)
        missing_sections = self._find_missing_sections(prompt_sections)
        warnings = self._build_warnings(prompt, scene_plan)
        suggestions = self._build_suggestions(
            duplicate_keywords,
            missing_sections,
            warnings,
        )
        quality_score = self._score(
            prompt,
            duplicate_keywords,
            missing_sections,
        )

        print(f"[PromptCritic] Quality score: {quality_score}")
        print(f"[PromptCritic] Duplicate: {duplicate_keywords}")
        print(f"[PromptCritic] Missing: {missing_sections}")

        return {
            "duplicate_keywords": duplicate_keywords,
            "missing_sections": missing_sections,
            "warnings": warnings,
            "quality_score": quality_score,
            "suggestions": suggestions,
        }

    def _apply_reasoning(self, state, fallback_report):
        system_prompt = (
            "You are a prompt critic. Return only JSON with keys: "
            "duplicate_keywords, missing_sections, warnings, quality_score, suggestions. "
            "Do not include markdown."
        )
        user_prompt = dumps_payload(
            {
                "task": "prompt_critic",
                "canonical_prompt": state.get("canonical_prompt") or state.get("final_prompt"),
                "prompt_sections": state.get("prompt_sections"),
                "scene_plan": state.get("scene_plan"),
                "fallback_report": fallback_report,
            }
        )
        result = self.reasoner_router.reason(
            system_prompt,
            user_prompt,
            fallback=fallback_report,
            schema_name="prompt_report",
        )
        return {
            "duplicate_keywords": self._as_list(
                result.get("duplicate_keywords", fallback_report.get("duplicate_keywords", []))
            ),
            "missing_sections": self._as_list(
                result.get("missing_sections", fallback_report.get("missing_sections", []))
            ),
            "warnings": self._as_list(result.get("warnings", fallback_report.get("warnings", []))),
            "quality_score": self._as_int(
                result.get("quality_score", fallback_report.get("quality_score", 100)),
                default=fallback_report.get("quality_score", 100),
            ),
            "suggestions": self._as_list(
                result.get("suggestions", fallback_report.get("suggestions", []))
            ),
            "reasoning_provider": result.get("reasoning_provider"),
            "reasoning_used_fallback": result.get("reasoning_used_fallback"),
            "reasoning_latency": result.get("reasoning_latency"),
            "reasoning_fallback_reason": result.get("reasoning_fallback_reason"),
        }

    def _find_duplicate_keywords(self, prompt):
        text = prompt.lower()
        duplicates = []
        for keyword in self.DUPLICATE_KEYWORDS:
            count = text.count(keyword)
            if count > 1:
                duplicates.append({"keyword": keyword, "count": count})
        return duplicates

    def _find_missing_sections(self, prompt_sections):
        missing = []
        for label, keys in self.REQUIRED_SECTIONS.items():
            if not any(self._has_value(prompt_sections.get(key)) for key in keys):
                missing.append(label)
        return missing

    def _has_value(self, value):
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, dict):
            return any(self._has_value(item) for item in value.values())
        if isinstance(value, list):
            return any(self._has_value(item) for item in value)
        return True

    def _build_warnings(self, prompt, scene_plan):
        words = prompt.replace("\n", " ").split()
        warnings = []
        if len(words) < 20:
            warnings.append("prompt is too short")
        if len(words) > 120:
            warnings.append("prompt is too long")

        if isinstance(scene_plan, dict):
            if not scene_plan.get("interaction"):
                warnings.append("character interaction may be unclear")
            if not scene_plan.get("scene_type"):
                warnings.append("scene description may be weak")
        return warnings

    def _build_suggestions(self, duplicate_keywords, missing_sections, warnings):
        suggestions = []
        if duplicate_keywords:
            suggestions.append("Remove duplicated keywords")
            suggestions.append("Simplify repetitive quality tags")
        if "Layout" in missing_sections:
            suggestions.append("Add clearer composition")
        if "Character" in missing_sections or "Pose" in missing_sections:
            suggestions.append("Add character interaction")
        if "prompt is too long" in warnings:
            suggestions.append("Shorten the prompt before provider adaptation")
        if "prompt is too short" in warnings:
            suggestions.append("Add essential subject, style, layout, and lighting details")
        return suggestions

    def _score(self, prompt, duplicate_keywords, missing_sections):
        words = prompt.replace("\n", " ").split()
        score = 100
        score -= len(duplicate_keywords) * 5
        score -= len(missing_sections) * 10
        if len(words) > 120:
            score -= 5
        if len(words) < 20:
            score -= 15
        return max(0, score)

    def _as_list(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def _as_int(self, value, default=100):
        try:
            return int(value)
        except (TypeError, ValueError):
            return int(default)
