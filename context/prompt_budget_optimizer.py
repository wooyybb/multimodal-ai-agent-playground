import re


class PromptBudgetOptimizer:
    LOW_PRIORITY_MARKERS = (
        "clear subject",
        "clear subject presentation",
        "coherent scene",
        "create a coherent visual scene",
        "flexible",
        "single clear frame",
        "priority",
        "score",
        "each uploaded image represents",
        "do not merge characters",
    )

    def optimize(self, phrases, max_tokens: int, high_priority=None) -> dict:
        high_priority = tuple(term.lower() for term in (high_priority or ()))
        kept = []
        removed = []
        token_count = 0

        ordered = sorted(
            self._unique(phrases),
            key=lambda phrase: self._priority_rank(phrase, high_priority),
        )
        for phrase in ordered:
            tokens = self.count_tokens(phrase)
            if token_count + tokens <= max_tokens:
                kept.append(phrase)
                token_count += tokens
            else:
                removed.append(phrase)

        return {
            "phrases": kept,
            "prompt": ", ".join(kept),
            "token_count": self.count_tokens(", ".join(kept)),
            "removed_low_priority_phrases": removed,
            "passed_token_budget": self.count_tokens(", ".join(kept)) <= max_tokens,
        }

    def count_tokens(self, text):
        return len(re.findall(r"\w+|[^\w\s]", str(text or "")))

    def _priority_rank(self, phrase, high_priority):
        lowered = str(phrase or "").lower()
        if any(term and term in lowered for term in high_priority):
            return 0
        if any(marker in lowered for marker in self.LOW_PRIORITY_MARKERS):
            return 2
        return 1

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
