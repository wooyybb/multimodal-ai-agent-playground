class ProviderRenderer:
    IDENTITY_TERMS = (
        "gender",
        "hair",
        "hairstyle",
        "eye color",
        "eyes",
        "outfit",
        "clothing",
        "clothes",
        "accessory",
        "accessories",
        "female",
        "male",
        "woman",
        "man",
        "girl",
        "boy",
    )

    def render(self, program: dict, provider: str = "flux") -> dict:
        provider = str(provider or "flux").lower()
        generation_prompt = (
            self.render_sdxl(program)
            if provider in {"sdxl", "sdxl_quality"}
            else self.render_flux(program)
        )
        return {
            "generation_prompt": generation_prompt,
            "sdxl_style_prompt": self.render_sdxl(program),
            "clip_prompt": self.render_clip(program),
            "pickscore_prompt": self.render_pickscore(program),
            "vlm_judge_prompt": self.render_vlm_judge(program),
            "negative_prompt": self.render_negative(program),
            "provider_render_report": {
                "provider": provider,
                "generation_strategy": "style_prompt"
                if provider in {"sdxl", "sdxl_quality"}
                else "dense_prompt",
            },
        }

    def render_flux(self, program):
        return self._join(
            [
                program.get("identity", []),
                program.get("scene", []),
                program.get("style", []),
                program.get("layout", []),
                program.get("lighting", []),
                program.get("quality", []),
            ]
        )

    def render_sdxl(self, program):
        values = (
            program.get("style", [])
            + program.get("layout", [])
            + program.get("lighting", [])
            + program.get("quality", [])
        )
        values = [
            value
            for value in values
            if not any(term in str(value).lower() for term in self.IDENTITY_TERMS)
        ]
        return self._join(values, max_items=18)

    def render_clip(self, program):
        return self._join(
            [
                program.get("identity", [])[:2],
                program.get("scene", [])[:2],
                program.get("layout", [])[:3],
            ],
            max_items=8,
        )

    def render_pickscore(self, program):
        return self._join(
            [
                program.get("style", []),
                program.get("layout", []),
                program.get("lighting", []),
                program.get("quality", []),
                "appealing composition",
                "coherent style",
            ]
        )

    def render_vlm_judge(self, program):
        prompt = (
            "Compare reference and generated image for identity, style, lighting, "
            "camera, composition, background, and prompt alignment."
        )
        return self._join([prompt, self.render_flux(program)])

    def render_negative(self, program):
        return self._join(program.get("negative", []))

    def _join(self, values, max_items=None):
        flat = []
        self._append(flat, values)
        result = []
        seen = set()
        for item in flat:
            text = str(item or "").strip(" ,.")
            key = text.lower()
            if text and key not in seen:
                result.append(text)
                seen.add(key)
        if max_items:
            result = result[:max_items]
        return ", ".join(result)

    def _append(self, values, value):
        if value is None:
            return
        if isinstance(value, str):
            values.append(value)
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                self._append(values, item)
            return
        if isinstance(value, dict):
            for item in value.values():
                self._append(values, item)
            return
        values.append(value)
