class ContextProgramValidator:
    REQUIRED_KEYS = [
        "task",
        "user_goal",
        "scene",
        "characters",
        "style",
        "layout",
        "pose",
        "expression",
        "lighting",
        "quality",
        "negative",
        "memory",
        "retrieval",
        "provider",
        "output",
    ]

    EXPECTED_TYPES = {
        "task": dict,
        "user_goal": dict,
        "scene": dict,
        "characters": dict,
        "style": dict,
        "layout": dict,
        "pose": dict,
        "expression": dict,
        "lighting": dict,
        "quality": dict,
        "negative": dict,
        "memory": dict,
        "retrieval": dict,
        "provider": dict,
        "output": dict,
    }

    def run(self, state: dict) -> dict:
        print("[ContextProgramValidator] Running...")
        state = state or {}
        context_program = state.get("context_program") or {}
        provider = self._provider(state, context_program)

        missing_keys = self._missing_keys(context_program)
        type_warnings = self._type_warnings(context_program)
        provider_warnings = self._provider_warnings(
            provider,
            context_program,
            state.get("user_prompt", ""),
        )
        suggestions = self._suggestions(missing_keys, type_warnings, provider_warnings)
        score = self._score(missing_keys, type_warnings, provider_warnings)
        valid = not missing_keys and not type_warnings

        result = {
            "valid": valid,
            "missing_keys": missing_keys,
            "type_warnings": type_warnings,
            "provider_warnings": provider_warnings,
            "suggestions": suggestions,
            "score": score,
        }

        print(f"[ContextProgramValidator] Valid: {valid}")
        print(f"[ContextProgramValidator] Score: {score}")
        print(
            "[ContextProgramValidator] Warnings: "
            f"{len(type_warnings) + len(provider_warnings)}"
        )
        return {"context_validation": result}

    def _provider(self, state, context_program):
        provider_section = context_program.get("provider") or {}
        provider = (
            state.get("provider")
            or provider_section.get("selected_provider")
            or provider_section.get("requested_provider")
            or "flux"
        )
        return str(provider).lower()

    def _missing_keys(self, context_program):
        if not isinstance(context_program, dict):
            return list(self.REQUIRED_KEYS)
        return [key for key in self.REQUIRED_KEYS if key not in context_program]

    def _type_warnings(self, context_program):
        if not isinstance(context_program, dict):
            return ["context_program should be a dict"]

        warnings = []
        for key, expected_type in self.EXPECTED_TYPES.items():
            if key not in context_program:
                continue
            if not isinstance(context_program.get(key), expected_type):
                warnings.append(f"{key} should be {expected_type.__name__}")

        characters = context_program.get("characters")
        if isinstance(characters, dict):
            character_items = characters.get("characters", [])
            if character_items is not None and not isinstance(character_items, list):
                warnings.append("characters.characters should be list")

        for key in ("style", "pose", "expression", "lighting", "negative"):
            section = context_program.get(key)
            if isinstance(section, dict):
                self._check_list_values(key, section, warnings)

        return warnings

    def _check_list_values(self, section_name, section, warnings):
        list_like_keys = {
            "style": ("style_keywords", "rendering_rules"),
            "pose": ("pose_rules", "avoid"),
            "expression": ("expression_rules", "avoid"),
            "lighting": ("lighting_keywords",),
            "negative": ("negative_prompt", "strict_avoid"),
        }
        for key in list_like_keys.get(section_name, ()):
            value = section.get(key)
            if value is not None and not isinstance(value, list):
                warnings.append(f"{section_name}.{key} should be list")

    def _provider_warnings(self, provider, context_program, user_prompt):
        warnings = []
        quality = context_program.get("quality") or {}
        negative = context_program.get("negative") or {}
        hint = str(quality.get("prompt_budget_hint") or "")
        negative_prompt = negative.get("negative_prompt") or []

        if provider == "flux":
            if len(hint.split()) > 20 or len(str(user_prompt or "").split()) > 80:
                warnings.append(
                    "flux does not support long prompts; keep prompt_budget_hint compact"
                )
            if negative_prompt:
                warnings.append(
                    "flux path keeps negative_prompt in state but does not apply it directly to generation"
                )
        elif provider == "sdxl":
            if not negative_prompt:
                warnings.append("sdxl should include a negative section")
        elif provider == "gpt_image":
            warnings.append("gpt_image can use long structured prompts")
        else:
            warnings.append(f"unknown provider '{provider}' will need routing fallback")

        return warnings

    def _suggestions(self, missing_keys, type_warnings, provider_warnings):
        suggestions = []
        if missing_keys:
            suggestions.append("rebuild context_program with all required sections")
        if type_warnings:
            suggestions.append("normalize context_program section types before assembly")
        if provider_warnings:
            suggestions.append("review provider-specific prompt constraints")
        if not suggestions:
            suggestions.append("context_program is ready for prompt assembly")
        return suggestions

    def _score(self, missing_keys, type_warnings, provider_warnings):
        score = 100
        score -= len(missing_keys) * 5
        score -= len(type_warnings) * 4
        score -= len(provider_warnings) * 3
        return max(0, min(100, score))
