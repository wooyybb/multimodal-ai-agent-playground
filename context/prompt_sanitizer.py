import re


class PromptSanitizer:
    SEMANTIC_GROUPS = (
        (("anime", "anime style", "anime illustration"), "anime illustration"),
        (
            ("balanced", "balanced subject placement", "balanced composition"),
            "balanced composition",
        ),
        (("woman", "female", "human face"), "female character"),
        (("sword", "weapon", "holding a sword"), "holding a sword"),
    )

    def sanitize(
        self,
        prompt: str,
        forbidden_concepts=None,
        provider: str = "flux",
        max_tokens: int | None = None,
    ) -> dict:
        forbidden_concepts = list(forbidden_concepts or [])
        original = str(prompt or "")
        phrases = self._split_phrases(original)
        removed_forbidden = []
        deduplicated = []
        semantic_merges = []

        clean_phrases = []
        seen = set()
        for phrase in phrases:
            if self._has_forbidden(phrase, forbidden_concepts):
                removed_forbidden.append(phrase)
                continue
            merged = self._semantic_merge(phrase, forbidden_concepts)
            if merged != phrase:
                semantic_merges.append({"from": phrase, "to": merged})
            key = merged.lower()
            if key in seen:
                deduplicated.append(merged)
                continue
            clean_phrases.append(merged)
            seen.add(key)

        prompt_text = ", ".join(clean_phrases)
        prompt_text, trimmed = self._enforce_budget(prompt_text, max_tokens)
        return {
            "prompt": prompt_text,
            "prompt_sanitizer_report": {
                "provider": provider,
                "removed_forbidden": removed_forbidden,
                "deduplicated_phrases": deduplicated,
                "semantic_merges": semantic_merges,
                "token_budget": max_tokens,
                "token_count": self.count_tokens(prompt_text),
                "trimmed": trimmed,
            },
        }

    def merge_negative_prompt(self, user_negative, system_negative):
        values = []
        for item in (user_negative, system_negative):
            if isinstance(item, str):
                values.extend(self._split_phrases(item))
            elif isinstance(item, (list, tuple)):
                values.extend(str(value) for value in item if str(value).strip())
        return ", ".join(self._unique(values))

    def count_tokens(self, prompt):
        return len(re.findall(r"\w+|[^\w\s]", str(prompt or "")))

    def _split_phrases(self, prompt):
        phrases = re.split(r",|\n|;", str(prompt or ""))
        return [" ".join(phrase.split()).strip(" ,.") for phrase in phrases if phrase.strip()]

    def _has_forbidden(self, phrase, forbidden_concepts):
        lowered = phrase.lower()
        return any(str(term).lower() in lowered for term in forbidden_concepts if term)

    def _semantic_merge(self, phrase, forbidden_concepts):
        lowered = phrase.lower()
        forbidden = {str(term).lower() for term in forbidden_concepts or []}
        for aliases, canonical in self.SEMANTIC_GROUPS:
            if canonical == "holding a sword" and any(
                term in forbidden for term in ("weapon", "sword", "holding a sword")
            ):
                return phrase
            if any(alias == lowered or alias in lowered for alias in aliases):
                return canonical
        return phrase

    def _enforce_budget(self, prompt, max_tokens):
        if not max_tokens:
            return prompt, False
        tokens = self._split_tokenish(prompt)
        if len(tokens) <= max_tokens:
            return prompt, False
        kept = []
        count = 0
        for phrase in self._split_phrases(prompt):
            phrase_tokens = self._split_tokenish(phrase)
            if count + len(phrase_tokens) > max_tokens:
                continue
            kept.append(phrase)
            count += len(phrase_tokens)
        if not kept:
            kept = [" ".join(tokens[:max_tokens])]
        return ", ".join(kept), True

    def _split_tokenish(self, prompt):
        return re.findall(r"\w+|[^\w\s]", str(prompt or ""))

    def _unique(self, values):
        unique = []
        seen = set()
        for value in values:
            item = str(value or "").strip(" ,.")
            key = item.lower()
            if item and key not in seen:
                unique.append(item)
                seen.add(key)
        return unique
