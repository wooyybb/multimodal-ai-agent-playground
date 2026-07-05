class StyleProgramBuilder:
    STYLE_PRESETS = {
        "ghibli": {
            "style_prompt": "warm hand-painted animation background, soft natural colors",
            "lora_name": "ghibli",
            "lora_scale": 0.75,
            "lighting": "soft warm cinematic light",
            "color_palette": ["warm green", "cream", "soft blue"],
        },
        "anime": {
            "style_prompt": "clean anime illustration, expressive character design",
            "lora_name": "anime",
            "lora_scale": 0.7,
            "lighting": "clean cel-shaded lighting",
            "color_palette": ["pastel", "clear skin tone", "accent color"],
        },
        "watercolor": {
            "style_prompt": "watercolor texture, soft pigment edges, paper grain",
            "lora_name": "watercolor",
            "lora_scale": 0.65,
            "lighting": "diffuse natural light",
            "color_palette": ["muted pastel", "paper white", "soft wash"],
        },
        "realistic": {
            "style_prompt": "realistic portrait rendering, natural skin and fabric detail",
            "lora_name": "realistic",
            "lora_scale": 0.6,
            "lighting": "natural studio lighting",
            "color_palette": ["neutral", "skin tone", "realistic fabric color"],
        },
    }

    def build(self, state: dict, quality_mode: bool = False) -> dict:
        state = state or {}
        style_name = self._style_name(state)
        preset = dict(self.STYLE_PRESETS.get(style_name, self.STYLE_PRESETS["anime"]))
        return {
            "style_name": style_name,
            "style_prompt": preset["style_prompt"],
            "lora_name": preset["lora_name"],
            "lora_scale": preset["lora_scale"],
            "lighting": preset["lighting"],
            "color_palette": preset["color_palette"],
            "quality_mode": bool(quality_mode),
        }

    def _style_name(self, state):
        text = self._style_text(state)
        for name in self.STYLE_PRESETS:
            if name in text:
                return name
        if "webtoon" in text or "manga" in text:
            return "anime"
        if "photo" in text or "realistic" in text:
            return "realistic"
        return "anime"

    def _style_text(self, state):
        context_program = state.get("context_program") or {}
        reference_image = state.get("reference_image") or {}
        style = context_program.get("style") or {}
        reference_style = reference_image.get("style") if isinstance(reference_image, dict) else {}
        return " ".join(
            str(item or "").lower()
            for item in (
                state.get("user_prompt"),
                style,
                reference_style,
                state.get("generation_prompt"),
                state.get("provider_prompt"),
            )
        )
