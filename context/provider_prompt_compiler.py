import re

from context.prompt_budget_optimizer import PromptBudgetOptimizer


class ProviderPromptCompiler:
    INTERNAL_PATTERNS = (
        r"\b(identity|style|composition)\s+priority\s*[:=]?\s*\d+(?:\.\d+)?\b",
        r"\bpriority\s*[:=]?\s*\d+(?:\.\d+)?\b",
        r"\bscore\s*[:=]?\s*\d+(?:\.\d+)?\b",
        r"each uploaded image represents[^,.;]*",
        r"do not merge characters",
        r"create a coherent visual scene",
        r"clear subject presentation",
        r"single clear frame",
        r"\bflexible\b",
    )
    WEAK_PHRASES = (
        "clear subject",
        "clear subject presentation",
        "coherent scene",
        "create a coherent visual scene",
        "flexible",
        "single clear frame",
    )
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
    SYSTEM_NEGATIVE = (
        "low quality",
        "blurry",
        "bad anatomy",
        "duplicate subject",
        "extra fingers",
        "distorted face",
    )

    def __init__(self):
        self.optimizer = PromptBudgetOptimizer()

    def compile(
        self,
        semantic_program: dict,
        provider: str = "flux",
        forbidden_concepts=None,
        negative_prompt=None,
    ) -> dict:
        self._removed_internal = []
        self._removed_forbidden = []
        self._removed_duplicates = []
        provider = str(provider or "flux").lower()
        forbidden_concepts = list(forbidden_concepts or [])
        sections = self._sections(semantic_program)
        negative = self._negative_prompt(
            sections.get("negative", []),
            negative_prompt,
            forbidden_concepts,
        )
        flux = self._compile_flux(sections, forbidden_concepts)
        sdxl = self._compile_sdxl(sections, forbidden_concepts)
        clip = self._compile_clip(sections, forbidden_concepts)
        pickscore = self._compile_pickscore(sections, forbidden_concepts)
        vlm = self._compile_vlm_judge(flux["prompt"])
        prompt_type = "style_prompt" if provider in {"sdxl", "sdxl_quality"} else "dense_prompt"
        generation_prompt = sdxl["prompt"] if prompt_type == "style_prompt" else flux["prompt"]

        report = {
            "provider": provider,
            "prompt_type": prompt_type,
            "token_count": self.optimizer.count_tokens(generation_prompt),
            "sdxl_token_count": sdxl["token_count"],
            "clip_token_count": clip["token_count"],
            "removed_low_priority_phrases": sdxl["removed_low_priority_phrases"],
            "removed_internal_control_tokens": self._unique(
                flux["removed_internal_control_tokens"]
                + sdxl["removed_internal_control_tokens"]
                + clip["removed_internal_control_tokens"]
                + self._removed_internal
            ),
            "duplicate_phrases_removed": self._unique(
                flux["duplicate_phrases_removed"]
                + sdxl["duplicate_phrases_removed"]
                + clip["duplicate_phrases_removed"]
                + self._removed_duplicates
            ),
            "forbidden_concepts_removed": self._unique(
                flux["forbidden_concepts_removed"]
                + sdxl["forbidden_concepts_removed"]
                + clip["forbidden_concepts_removed"]
                + self._removed_forbidden
            ),
            "passed_token_budget": sdxl["token_count"] <= 77 and clip["token_count"] <= 77,
        }
        return {
            "generation_prompt": generation_prompt,
            "flux_prompt": flux["prompt"],
            "sdxl_style_prompt": sdxl["prompt"],
            "clip_prompt": clip["prompt"],
            "pickscore_prompt": pickscore["prompt"],
            "vlm_judge_prompt": vlm,
            "negative_prompt": negative["prompt"],
            "provider_prompt_compiler_report": report,
            "provider_render_report": report,
        }

    def _compile_flux(self, sections, forbidden):
        phrases = self._clean_phrases(
            sections.get("identity", [])
            + sections.get("scene", [])
            + sections.get("style", [])
            + sections.get("layout", [])
            + sections.get("lighting", [])
            + sections.get("quality", []),
            forbidden,
        )
        return self._prompt_result(phrases, max_tokens=140)

    def _compile_sdxl(self, sections, forbidden):
        identity = self._minimal_identity(sections.get("identity", []))
        phrases = self._clean_phrases(
            identity
            + sections.get("style", [])
            + sections.get("lighting", [])
            + sections.get("layout", [])
            + sections.get("quality", []),
            forbidden,
            remove_identity=True,
        )
        optimized = self.optimizer.optimize(
            phrases,
            max_tokens=60,
            high_priority=(
                "anime",
                "webtoon",
                "watercolor",
                "render",
                "palette",
                "lighting",
                "consistent character design",
                "composition",
            ),
        )
        result = self._prompt_result(optimized["phrases"], max_tokens=77)
        result["removed_low_priority_phrases"] = optimized["removed_low_priority_phrases"]
        result["token_count"] = optimized["token_count"]
        return result

    def _compile_clip(self, sections, forbidden):
        phrases = self._clean_phrases(
            sections.get("identity", [])[:2]
            + sections.get("scene", [])[:2]
            + sections.get("layout", [])[:2]
            + sections.get("style", [])[:2],
            forbidden,
            remove_quality=True,
        )
        optimized = self.optimizer.optimize(phrases, max_tokens=40)
        result = self._prompt_result(optimized["phrases"], max_tokens=40)
        result["removed_low_priority_phrases"] = optimized["removed_low_priority_phrases"]
        result["token_count"] = optimized["token_count"]
        return result

    def _compile_pickscore(self, sections, forbidden):
        phrases = self._clean_phrases(
            sections.get("style", [])
            + sections.get("layout", [])
            + sections.get("lighting", [])
            + sections.get("quality", [])
            + ["appealing composition", "cohesive visual style"],
            forbidden,
        )
        return self._prompt_result(phrases, max_tokens=90)

    def _compile_vlm_judge(self, flux_prompt):
        return (
            "Compare reference and generated image for identity, style, lighting, "
            "camera, composition, background, and prompt alignment. Prompt: "
            f"{flux_prompt}"
        )

    def _prompt_result(self, phrases, max_tokens):
        cleaned = self._unique(phrases)
        prompt = ", ".join(cleaned)
        prompt, removed_budget = self._truncate_prompt(prompt, max_tokens)
        final_phrases = self._split(prompt)
        return {
            "prompt": prompt,
            "token_count": self.optimizer.count_tokens(prompt),
            "removed_low_priority_phrases": removed_budget,
            "removed_internal_control_tokens": [],
            "duplicate_phrases_removed": [
                phrase for phrase in cleaned if phrase not in final_phrases
            ],
            "forbidden_concepts_removed": [],
        }

    def _clean_phrases(
        self,
        values,
        forbidden,
        remove_identity=False,
        remove_quality=False,
    ):
        phrases = []
        for value in self._flatten(values):
            for phrase in self._split(value):
                cleaned, removed_internal = self._remove_internal(phrase)
                if removed_internal:
                    self._removed_internal.extend(removed_internal)
                if not cleaned or removed_internal:
                    continue
                lowered = cleaned.lower()
                if any(term.lower() in lowered for term in forbidden):
                    self._removed_forbidden.append(cleaned)
                    continue
                if any(weak in lowered for weak in self.WEAK_PHRASES):
                    continue
                if remove_identity and any(term in lowered for term in self.IDENTITY_TERMS):
                    continue
                if remove_quality and self._is_quality_only(lowered):
                    continue
                phrases.append(self._canonical(cleaned))
        return self._unique_tracking_duplicates(phrases)

    def _negative_prompt(self, semantic_negative, user_negative, forbidden):
        phrases = self._clean_phrases(
            list(semantic_negative or [])
            + self._flatten(user_negative)
            + list(forbidden or [])
            + list(self.SYSTEM_NEGATIVE),
            forbidden=[],
        )
        return {"prompt": ", ".join(self._unique(phrases))}

    def _sections(self, program):
        program = program or {}
        return {
            key: self._flatten(program.get(key, []))
            for key in (
                "identity",
                "style",
                "layout",
                "scene",
                "lighting",
                "quality",
                "negative",
                "constraints",
            )
        }

    def _minimal_identity(self, identity):
        text = " ".join(str(item).lower() for item in identity or [])
        phrases = []
        if any(term in text for term in ("two", "pair", "couple", "friends", "group")):
            phrases.append("two characters")
        elif any(term in text for term in ("woman", "man", "girl", "boy", "female", "male", "character")):
            phrases.append("character portrait")
        if text:
            phrases.append("consistent character design")
        return phrases

    def _remove_internal(self, phrase):
        text = str(phrase or "")
        removed = []
        for pattern in self.INTERNAL_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                removed.append(text)
                text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        text = " ".join(text.split()).strip(" ,.")
        return text, removed

    def _truncate_prompt(self, prompt, max_tokens):
        if self.optimizer.count_tokens(prompt) <= max_tokens:
            return prompt, []
        phrases = self._split(prompt)
        optimized = self.optimizer.optimize(phrases, max_tokens=max_tokens)
        return optimized["prompt"], optimized["removed_low_priority_phrases"]

    def _canonical(self, phrase):
        lowered = str(phrase or "").strip(" ,.").lower()
        groups = (
            (("anime", "anime style", "anime illustration"), "anime illustration"),
            (("balanced", "balanced layout", "balanced composition"), "balanced composition"),
            (("ultra detailed", "highly detailed"), "detailed rendering"),
        )
        for aliases, canonical in groups:
            if lowered in aliases or any(alias in lowered for alias in aliases):
                return canonical
        return str(phrase or "").strip(" ,.")

    def _is_quality_only(self, lowered):
        return any(
            term in lowered
            for term in (
                "masterpiece",
                "8k",
                "ultra detailed",
                "best quality",
                "high quality",
                "negative",
                "bad anatomy",
                "blurry",
            )
        )

    def _flatten(self, value):
        result = []
        if value is None:
            return result
        if isinstance(value, str):
            return [value]
        if isinstance(value, (list, tuple, set)):
            for item in value:
                result.extend(self._flatten(item))
            return result
        if isinstance(value, dict):
            for item in value.values():
                result.extend(self._flatten(item))
            return result
        return [str(value)]

    def _split(self, value):
        return [
            " ".join(part.split()).strip(" ,.")
            for part in re.split(r",|\n|;", str(value or ""))
            if part.strip()
        ]

    def _unique(self, phrases):
        result = []
        seen = set()
        for phrase in phrases or []:
            text = str(phrase or "").strip(" ,.")
            key = text.lower()
            if text and key not in seen:
                result.append(text)
                seen.add(key)
        return result

    def _unique_tracking_duplicates(self, phrases):
        result = []
        seen = set()
        for phrase in phrases or []:
            text = str(phrase or "").strip(" ,.")
            key = text.lower()
            if not text:
                continue
            if key in seen:
                self._removed_duplicates.append(text)
                continue
            result.append(text)
            seen.add(key)
        return result
