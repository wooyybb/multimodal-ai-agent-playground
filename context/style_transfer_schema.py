class StyleTransferSchema:
    DEFAULT_NEGATIVE = ["low quality", "blurry", "bad anatomy", "duplicate subject"]

    def from_rule_program_v4(self, program: dict) -> dict:
        program = program or {}
        style = program.get("style") or {}
        layout = program.get("layout") or {}
        character_rules = program.get("character_rules") or {}
        text_rules = program.get("text_rules") or {}
        pose_expression = program.get("pose_expression") or {}
        return {
            "task": {
                "type": "reference_aware_style_transfer",
                "goal": style.get("name")
                or "preserve reference identity while applying requested style",
            },
            "identity": {
                "preserve_identity": bool(character_rules.get("preserve_identity", True)),
                "preserve_outfit": bool(character_rules.get("preserve_outfit", True)),
                "preserve_hairstyle": bool(
                    character_rules.get("preserve_hairstyle", True)
                ),
                "preserve_palette": True,
            },
            "style": {
                "renderer": style.get("rendering") or style.get("name", ""),
                "anime_strength": self._strength_from_style(style),
                "lighting": style.get("lighting", ""),
                "palette": ", ".join(style.get("color_palette", []))
                if isinstance(style.get("color_palette"), list)
                else style.get("color_palette", ""),
                "texture": style.get("texture", ""),
            },
            "layout": {
                "camera": layout.get("camera", ""),
                "composition": layout.get("structure", ""),
                "panel_type": layout.get("format", ""),
                "panel_count": self._panel_count(layout),
            },
            "scene": {
                "background": layout.get("background", ""),
                "decorations": layout.get("decorations", []),
                "mood": style.get("mood", ""),
            },
            "pose": {
                "interaction": ", ".join(pose_expression.get("allowed", []))
                if isinstance(pose_expression.get("allowed"), list)
                else "",
                "energy": "",
                "naturalness": "natural",
            },
            "text": {
                "enabled": bool(text_rules.get("allow_small_text", True)),
                "style": "",
                "language": ", ".join(text_rules.get("language_constraints", []))
                if isinstance(text_rules.get("language_constraints"), list)
                else "",
            },
            "negative": {
                "remove": list(program.get("forbidden_concepts") or []),
            },
            "generation_strategy": {
                "identity_strength": 1.0,
                "style_strength": 0.8,
                "composition_strength": 0.7,
            },
        }

    def normalize_v4_requirement(self, candidate: dict, fallback: dict) -> dict:
        candidate = candidate or {}
        if self._looks_like_reasoner_metadata(candidate):
            candidate = {}
        output = self._deep_merge(fallback or {}, candidate)
        output.setdefault("task", {}).setdefault("type", "reference_aware_style_transfer")
        output.setdefault("task", {}).setdefault("goal", "")
        output.setdefault("identity", {})
        output.setdefault("style", {})
        output.setdefault("layout", {})
        output.setdefault("scene", {})
        output.setdefault("pose", {})
        output.setdefault("text", {})
        output.setdefault("negative", {}).setdefault("remove", [])
        output.setdefault("generation_strategy", {})
        return output

    def v4_to_legacy_program(self, requirement: dict, fallback_program: dict) -> dict:
        requirement = self.normalize_v4_requirement(
            requirement,
            self.from_rule_program_v4(fallback_program),
        )
        fallback = dict(fallback_program or {})
        task = requirement.get("task") or {}
        identity = requirement.get("identity") or {}
        style = requirement.get("style") or {}
        layout = requirement.get("layout") or {}
        scene = requirement.get("scene") or {}
        pose = requirement.get("pose") or {}
        text = requirement.get("text") or {}
        negative = requirement.get("negative") or {}
        strategy = requirement.get("generation_strategy") or {}

        fallback["task_type"] = task.get("type", "reference_aware_style_transfer")
        fallback["style_goal"] = task.get("goal", "")
        fallback["character_rules"] = {
            "preserve_identity": bool(identity.get("preserve_identity", True)),
            "preserve_outfit": bool(identity.get("preserve_outfit", True)),
            "preserve_hairstyle": bool(identity.get("preserve_hairstyle", True)),
            "preserve_silhouette": bool(identity.get("preserve_identity", True)),
            "preserve_palette": bool(identity.get("preserve_palette", True)),
            "do_not_merge_characters": True,
        }
        fallback["identity_policy"] = identity
        fallback["style"] = {
            "name": task.get("goal", ""),
            "rendering": style.get("renderer", ""),
            "mood": scene.get("mood", ""),
            "color_palette": self._as_list(style.get("palette")),
            "texture": style.get("texture", ""),
            "lighting": style.get("lighting", ""),
            "anime_strength": style.get("anime_strength", 0),
        }
        fallback["layout"] = {
            "format": layout.get("panel_type", ""),
            "structure": layout.get("composition", ""),
            "camera": layout.get("camera", ""),
            "panel_count": layout.get("panel_count", 0),
            "background": scene.get("background", ""),
            "decorations": self._as_list(scene.get("decorations")),
        }
        fallback["pose_expression"] = {
            "allowed": [
                value
                for value in (
                    pose.get("interaction"),
                    pose.get("energy"),
                    pose.get("naturalness"),
                )
                if value
            ],
            "forbidden": [],
        }
        fallback["text_rules"] = {
            "allow_small_text": bool(text.get("enabled", True)),
            "avoid_large_typography": True,
            "style": text.get("style", ""),
            "language_constraints": self._as_list(text.get("language")),
        }
        fallback["generation_strategy"] = {
            "provider": "sdxl_quality",
            "use_img2img": True,
            "use_ip_adapter": True,
            "use_controlnet": True,
            "identity_strength": strategy.get("identity_strength", 1.0),
            "style_strength": strategy.get("style_strength", 0.8),
            "structure_strength": strategy.get(
                "composition_strength",
                strategy.get("structure_strength", 0.7),
            ),
        }
        fallback["forbidden_concepts"] = self._as_list(negative.get("remove"))
        fallback["negative_prompt"] = self._as_list(negative.get("remove")) + list(
            self.DEFAULT_NEGATIVE
        )
        fallback["requirement_program"] = requirement
        fallback["reasoning_summary"] = (
            f"Requirement Parser converted long prompt to JSON program: "
            f"{task.get('goal', '')}"
        )
        return fallback

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

    def _deep_merge(self, base, update):
        output = dict(base or {})
        for key, value in (update or {}).items():
            if isinstance(value, dict) and isinstance(output.get(key), dict):
                output[key] = self._deep_merge(output[key], value)
            elif value not in (None, "", []):
                output[key] = value
        return output

    def _looks_like_reasoner_metadata(self, candidate):
        useful = {
            "task",
            "identity",
            "style",
            "layout",
            "scene",
            "pose",
            "text",
            "negative",
            "generation_strategy",
        }
        return not any(key in candidate for key in useful)

    def _strength_from_style(self, style):
        text = " ".join(str(value).lower() for value in (style or {}).values())
        if "anime" in text or "webtoon" in text:
            return 0.8
        return 0.0

    def _panel_count(self, layout):
        text = " ".join(str(value).lower() for value in (layout or {}).values())
        if "four" in text or "4" in text:
            return 4
        return 0
