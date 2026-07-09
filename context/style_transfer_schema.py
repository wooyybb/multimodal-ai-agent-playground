class StyleTransferSchema:
    DEFAULT_NEGATIVE = ["low quality", "blurry", "bad anatomy", "duplicate subject"]

    def from_requirement_program(self, program: dict) -> dict:
        program = program or {}
        task = program.get("task") or {}
        identity = program.get("identity") or {}
        style = program.get("style") or {}
        layout = program.get("layout") or {}
        negative = program.get("negative") or {}
        strategy = program.get("generation_strategy") or {}
        return {
            "task_type": task.get("type", "reference_aware_style_transfer"),
            "style_goal": task.get("goal", ""),
            "identity_policy": {
                "preserve_identity": bool(identity.get("preserve_identity", True)),
                "preserve_hair": bool(identity.get("preserve_hairstyle", True)),
                "preserve_outfit": bool(identity.get("preserve_outfit", True)),
                "preserve_color_palette": bool(identity.get("preserve_palette", True)),
                "allow_minor_redraw": True,
            },
            "style": {
                "name": style.get("name", ""),
                "renderer": style.get("renderer", ""),
                "lineart": style.get("lineart", ""),
                "color_palette": style.get("palette", ""),
                "lighting": style.get("lighting", ""),
                "texture": style.get("texture", ""),
                "mood": style.get("mood", ""),
            },
            "layout": {
                "format": layout.get("format", ""),
                "composition": layout.get("composition", ""),
                "background": layout.get("background", ""),
                "decorations": layout.get("decorations", []),
            },
            "generation_strategy": {
                "provider": strategy.get("provider", "sdxl_quality"),
                "use_img2img": bool(strategy.get("use_img2img", True)),
                "use_ip_adapter": bool(strategy.get("use_ip_adapter", True)),
                "use_controlnet": bool(strategy.get("use_controlnet", False)),
                "style_strength": strategy.get("style_strength", 0.6),
                "identity_strength": strategy.get("identity_strength", 0.8),
                "structure_strength": strategy.get("structure_strength", 0.5),
            },
            "forbidden_concepts": list(negative.get("remove") or []),
            "negative_prompt": list(negative.get("remove") or self.DEFAULT_NEGATIVE),
            "reasoning_summary": program.get("reasoning_summary", ""),
        }

    def from_rule_program(self, program: dict) -> dict:
        program = program or {}
        style = program.get("style") or {}
        layout = program.get("layout") or {}
        character_rules = program.get("character_rules") or {}
        return {
            "task_type": "reference_aware_style_transfer",
            "style_goal": style.get("name") or "preserve reference identity while applying requested style",
            "identity_policy": {
                "preserve_identity": bool(character_rules.get("preserve_identity", True)),
                "preserve_hair": bool(character_rules.get("preserve_hairstyle", True)),
                "preserve_outfit": bool(character_rules.get("preserve_outfit", True)),
                "preserve_color_palette": True,
                "allow_minor_redraw": True,
            },
            "style": {
                "name": style.get("name", ""),
                "renderer": style.get("rendering", ""),
                "lineart": "",
                "color_palette": ", ".join(style.get("color_palette", []))
                if isinstance(style.get("color_palette"), list)
                else style.get("color_palette", ""),
                "lighting": "",
                "texture": style.get("texture", ""),
                "mood": style.get("mood", ""),
            },
            "layout": {
                "format": layout.get("format", ""),
                "composition": layout.get("structure", ""),
                "background": layout.get("background", ""),
                "decorations": layout.get("decorations", []),
            },
            "generation_strategy": {
                "provider": "sdxl_quality",
                "use_img2img": True,
                "use_ip_adapter": True,
                "use_controlnet": True,
                "style_strength": 0.45,
                "identity_strength": 0.75,
                "structure_strength": 0.60,
            },
            "forbidden_concepts": list(program.get("forbidden_concepts") or []),
            "negative_prompt": list(program.get("negative_prompt") or self.DEFAULT_NEGATIVE),
            "reasoning_summary": "Rule fallback converted to Style Transfer Program schema.",
        }

    def normalize(self, candidate: dict, fallback_program: dict) -> dict:
        if isinstance(candidate, dict) and "task" in candidate:
            candidate = self.from_requirement_program(candidate)
        fallback = self.from_rule_program(fallback_program)
        candidate = candidate or {}
        output = dict(fallback)
        for key in (
            "task_type",
            "style_goal",
            "forbidden_concepts",
            "negative_prompt",
            "reasoning_summary",
        ):
            if candidate.get(key) not in (None, "", []):
                output[key] = candidate.get(key)
        for key in ("identity_policy", "style", "layout", "generation_strategy"):
            value = candidate.get(key)
            if isinstance(value, dict):
                merged = dict(output.get(key) or {})
                merged.update({k: v for k, v in value.items() if v not in (None, "")})
                output[key] = merged
        output["task_type"] = "reference_aware_style_transfer"
        return output

    def to_legacy_program(self, llm_program: dict, fallback_program: dict) -> dict:
        if isinstance(llm_program, dict) and "task" in llm_program:
            llm_program = self.from_requirement_program(llm_program)
        llm_program = self.normalize(llm_program, fallback_program)
        fallback = dict(fallback_program or {})
        style = llm_program.get("style") or {}
        layout = llm_program.get("layout") or {}
        identity = llm_program.get("identity_policy") or {}
        strategy = llm_program.get("generation_strategy") or {}

        fallback["task_type"] = "reference_aware_style_transfer"
        fallback["style_goal"] = llm_program.get("style_goal", "")
        fallback["character_rules"] = {
            "preserve_identity": bool(identity.get("preserve_identity", True)),
            "preserve_outfit": bool(identity.get("preserve_outfit", True)),
            "preserve_hairstyle": bool(identity.get("preserve_hair", True)),
            "preserve_silhouette": bool(identity.get("preserve_identity", True)),
            "do_not_merge_characters": True,
        }
        fallback["identity_policy"] = identity
        fallback["style"] = {
            "name": style.get("name", ""),
            "rendering": style.get("renderer") or style.get("lineart") or "",
            "mood": style.get("mood", ""),
            "color_palette": self._as_list(style.get("color_palette")),
            "texture": style.get("texture", ""),
            "lighting": style.get("lighting", ""),
        }
        fallback["layout"] = {
            "format": layout.get("format", ""),
            "structure": layout.get("composition", ""),
            "background": layout.get("background", ""),
            "decorations": self._as_list(layout.get("decorations")),
        }
        fallback["generation_strategy"] = strategy
        fallback["forbidden_concepts"] = self._as_list(
            llm_program.get("forbidden_concepts")
        )
        fallback["negative_prompt"] = self._as_list(llm_program.get("negative_prompt"))
        fallback["reasoning_summary"] = llm_program.get("reasoning_summary", "")
        return fallback

    def _as_list(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return [value]
