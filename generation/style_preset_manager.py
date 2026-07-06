import os

from generation.generation_preset import GenerationPreset


class StylePresetManager:
    PRESETS = {
        "subtle_transfer": {
            "sdxl_strength": 0.30,
            "ip_adapter_scale": 0.55,
            "cfg": 5.5,
            "steps": 22,
            "reason": "Subtle style transfer keeps the reference image dominant.",
        },
        "balanced_transfer": {
            "sdxl_strength": 0.40,
            "ip_adapter_scale": 0.50,
            "cfg": 6.0,
            "steps": 24,
            "reason": "Balanced transfer keeps identity while allowing visible style change.",
        },
        "strong_style_transfer": {
            "sdxl_strength": 0.55,
            "ip_adapter_scale": 0.40,
            "cfg": 6.5,
            "steps": 28,
            "reason": "Strong style transfer gives the prompt more influence than the reference.",
        },
        "photobooth_soft": {
            "sdxl_strength": 0.38,
            "ip_adapter_scale": 0.50,
            "cfg": 5.8,
            "steps": 24,
            "reason": "Photobooth style benefits from soft changes and natural preservation.",
        },
        "ugly_cute_drawing": {
            "sdxl_strength": 0.62,
            "ip_adapter_scale": 0.35,
            "cfg": 6.8,
            "steps": 28,
            "reason": "Ugly-cute drawing requires stronger stylization and less identity lock.",
        },
        "anime_webtoon": {
            "sdxl_strength": 0.45,
            "ip_adapter_scale": 0.50,
            "cfg": 6.2,
            "steps": 26,
            "reason": "Anime/webtoon transfer balances stylization with identity preservation.",
        },
        "realistic_preserve": {
            "sdxl_strength": 0.32,
            "ip_adapter_scale": 0.60,
            "cfg": 5.5,
            "steps": 24,
            "reason": "Realistic preservation keeps the reference strong and reduces drift.",
        },
    }

    def select(self, state: dict) -> dict:
        print("[StylePresetManager] Selecting generation preset...")
        state = state or {}
        program = state.get("style_transfer_program") or {}
        preset_name, reason = self._select_name(state, program)
        preset_data = dict(self.PRESETS[preset_name])
        preset_data["reason"] = reason or preset_data["reason"]
        overrides = self._environment_overrides()
        preset_data.update(overrides)

        preset = GenerationPreset(
            preset_name=preset_name,
            sdxl_strength=float(preset_data["sdxl_strength"]),
            ip_adapter_scale=float(preset_data["ip_adapter_scale"]),
            cfg=float(preset_data["cfg"]),
            steps=int(preset_data["steps"]),
            width=int(preset_data.get("width", 768)),
            height=int(preset_data.get("height", 768)),
            reason=preset_data["reason"],
            environment_overrides=overrides,
        )
        result = preset.to_dict()
        print(f"[StylePresetManager] Selected preset: {result['preset_name']}")
        print(f"[StylePresetManager] Reason: {result['reason']}")
        print(f"[GenerationPreset] strength: {result['sdxl_strength']}")
        print(f"[GenerationPreset] ip_adapter_scale: {result['ip_adapter_scale']}")
        print(f"[GenerationPreset] cfg: {result['cfg']}")
        print(f"[GenerationPreset] steps: {result['steps']}")
        return result

    def _select_name(self, state, program):
        text = self._search_text(state, program)
        if self._has(text, ("photobooth", "인생네컷", "포토이즘", "photoism")):
            return "photobooth_soft", "Detected Korean photobooth style request."
        if self._has(
            text,
            ("ms paint", "ugly-cute", "childish lineart", "intentionally bad"),
        ):
            return "ugly_cute_drawing", "Detected intentionally rough ugly-cute drawing style."
        if self._has(text, ("anime", "webtoon")):
            return "anime_webtoon", "Detected anime or webtoon style request."
        if self._has(text, ("realistic", "photo-realistic", "photorealistic")):
            return "realistic_preserve", "Detected realistic preservation request."
        if self._has(
            text,
            ("strong style", "strong stylization", "dramatic style", "heavily stylized"),
        ):
            return "strong_style_transfer", "Detected strong style transfer request."
        if self._has(text, ("subtle", "preserve original", "keep original")):
            return "subtle_transfer", "Detected subtle preservation-focused request."
        return "balanced_transfer", "Default balanced style transfer preset."

    def _search_text(self, state, program):
        parts = [
            state.get("user_prompt"),
            state.get("caption"),
            (program.get("style") or {}).get("name"),
            (program.get("style") or {}).get("rendering"),
            (program.get("style") or {}).get("mood"),
            (program.get("style") or {}).get("texture"),
            (program.get("layout") or {}).get("structure"),
            (program.get("layout") or {}).get("background"),
        ]
        parts.extend((program.get("style") or {}).get("color_palette") or [])
        parts.extend((program.get("layout") or {}).get("decorations") or [])
        return " ".join(str(part or "") for part in parts).lower()

    def _has(self, text, keywords):
        return any(keyword.lower() in text for keyword in keywords)

    def _environment_overrides(self):
        mapping = {
            "SDXL_STRENGTH": ("sdxl_strength", float),
            "IP_ADAPTER_SCALE": ("ip_adapter_scale", float),
            "SDXL_CFG": ("cfg", float),
            "SDXL_STEPS": ("steps", int),
            "SDXL_WIDTH": ("width", int),
            "SDXL_HEIGHT": ("height", int),
        }
        overrides = {}
        for env_name, (field_name, caster) in mapping.items():
            value = os.getenv(env_name)
            if value in (None, ""):
                continue
            try:
                overrides[field_name] = caster(value)
            except (TypeError, ValueError):
                print(f"[StylePresetManager] Ignoring invalid {env_name}: {value}")
        return overrides
