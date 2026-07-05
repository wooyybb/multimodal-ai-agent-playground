import re


class FluxPromptRenderer:
    prompt_type = "Dense"

    def render(self, prompt: str, state: dict, plan: dict) -> dict:
        rendered = " ".join(str(prompt or "").split())
        return {
            "provider_prompt": rendered,
            "prompt_type": self.prompt_type,
            "word_count": self._word_count(rendered),
            "token_count": self._token_count(rendered),
            "notes": ["FLUX uses the existing dense visual prompt"],
        }

    def _word_count(self, prompt):
        return len(str(prompt or "").split())

    def _token_count(self, prompt):
        return len(re.findall(r"\w+|[^\w\s]", str(prompt or "")))


class SDXLPromptRenderer:
    prompt_type = "Style"
    IDENTITY_TERMS = {
        "identity",
        "gender",
        "girl",
        "boy",
        "woman",
        "man",
        "female",
        "male",
        "hair",
        "eye",
        "eyes",
        "outfit",
        "clothing",
        "clothes",
        "dress",
        "robe",
        "shirt",
        "accessory",
        "accessories",
        "weapon",
        "sword",
        "hat",
        "bag",
    }

    def render(self, prompt: str, state: dict, plan: dict) -> dict:
        style_program = plan.get("style_program") or state.get("style_program") or {}
        parts = [
            style_program.get("style_prompt"),
            style_program.get("lighting"),
            self._join(style_program.get("quality")),
            style_program.get("mood"),
            style_program.get("camera"),
            style_program.get("rendering"),
            self._join(style_program.get("color_palette")),
        ]
        rendered = self._clean(", ".join(part for part in parts if part))
        rendered = self._remove_identity_terms(rendered)
        rendered = self._limit_tokens(rendered, max_tokens=60)
        return {
            "provider_prompt": rendered,
            "style_prompt": rendered,
            "prompt_type": self.prompt_type,
            "word_count": self._word_count(rendered),
            "token_count": self._token_count(rendered),
            "notes": [
                "SDXL Img2Img uses reference image for identity",
                "SDXL prompt rendered from Style Program only",
                "identity, hair, outfit, eye color, and accessories removed from prompt",
            ],
        }

    def _join(self, value):
        if isinstance(value, (list, tuple)):
            return ", ".join(str(item) for item in value if item)
        return str(value or "")

    def _clean(self, prompt):
        return " ".join(str(prompt or "").replace("\n", " ").split()).strip(" ,")

    def _remove_identity_terms(self, prompt):
        phrases = []
        for phrase in str(prompt or "").split(","):
            words = {
                word.lower()
                for word in re.findall(r"[A-Za-z]+", phrase)
            }
            if words & self.IDENTITY_TERMS:
                continue
            cleaned = phrase.strip()
            if cleaned:
                phrases.append(cleaned)
        return ", ".join(phrases)

    def _limit_tokens(self, prompt, max_tokens):
        tokens = re.findall(r"\w+|[^\w\s]", str(prompt or ""))
        if len(tokens) <= max_tokens:
            return prompt
        limited = tokens[:max_tokens]
        text = " ".join(limited)
        text = text.replace(" ,", ",").replace(" .", ".")
        return text.strip(" ,")

    def _word_count(self, prompt):
        return len(str(prompt or "").split())

    def _token_count(self, prompt):
        return len(re.findall(r"\w+|[^\w\s]", str(prompt or "")))


class ProviderPromptRenderer:
    def render(self, provider_name: str, prompt: str, state: dict, plan: dict) -> dict:
        if provider_name == "sdxl_quality":
            return SDXLPromptRenderer().render(prompt, state, plan)
        return FluxPromptRenderer().render(prompt, state, plan)
