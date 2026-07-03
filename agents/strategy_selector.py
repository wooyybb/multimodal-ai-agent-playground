class StrategySelector:
    def run(self, state: dict) -> dict:
        print("[StrategySelector] Generating strategies...")
        state = state or {}
        score = float(state.get("score") or 0.0)
        reflection = str(state.get("reflection") or "")
        prompt = str(state.get("final_prompt") or "")
        caption = str(state.get("caption") or "")
        text = f"{reflection} {prompt} {caption}".lower()

        candidates = self._candidate_strategies(score, text)
        selected = max(candidates, key=lambda item: item.get("score", 0.0))
        print(f"[StrategySelector] Selected: {selected.get('id')} - {selected.get('title')}")
        return {
            "candidate_strategies": candidates,
            "selected_strategy": selected,
        }

    def _candidate_strategies(self, score, text):
        candidates = [
            self._identity_strategy(score, text),
            self._layout_strategy(score, text),
            self._lighting_strategy(score, text),
        ]
        if "style" in text or "anime" in text or "webtoon" in text:
            candidates.append(self._style_balance_strategy(score, text))
        return candidates

    def _identity_strategy(self, score, text):
        bonus = 0.12 if self._has_identity_signal(text) else 0.0
        return {
            "id": "S1",
            "title": "Increase identity preservation",
            "reason": "Reflection suggests subject or caption fidelity may be weak.",
            "expected_effect": "Keeps character identity, outfit, and accessories more stable.",
            "risk": "May reduce stylistic freedom.",
            "score": self._clamp(0.72 + bonus + self._low_score_bonus(score)),
        }

    def _layout_strategy(self, score, text):
        bonus = 0.15 if "layout" in text or "composition" in text else 0.0
        return {
            "id": "S2",
            "title": "Simplify composition and camera",
            "reason": "Layout or composition mismatch can reduce image-text alignment.",
            "expected_effect": "Improves framing, camera clarity, and subject placement.",
            "risk": "May make the image less dynamic.",
            "score": self._clamp(0.66 + bonus + self._low_score_bonus(score)),
        }

    def _lighting_strategy(self, score, text):
        bonus = 0.14 if "lighting" in text or "cinematic" in text else 0.0
        return {
            "id": "S3",
            "title": "Strengthen lighting coherence",
            "reason": "Lighting intent may not be visible enough in the generated image.",
            "expected_effect": "Makes mood and contrast easier for generation to follow.",
            "risk": "Could overpower character details if overemphasized.",
            "score": self._clamp(0.6 + bonus + (0.04 if score < 0.75 else 0.0)),
        }

    def _style_balance_strategy(self, score, text):
        bonus = 0.16 if "style conflict" in text or "conflict" in text else 0.06
        return {
            "id": "S4",
            "title": "Balance style against identity",
            "reason": "Requested style should support the subject rather than replace it.",
            "expected_effect": "Preserves style keywords while reducing identity drift.",
            "risk": "May produce a less stylized image.",
            "score": self._clamp(0.64 + bonus + self._low_score_bonus(score)),
        }

    def _has_identity_signal(self, text):
        return any(
            token in text
            for token in (
                "character",
                "subject",
                "caption",
                "identity",
                "face",
                "outfit",
                "accessories",
            )
        )

    def _low_score_bonus(self, score):
        if score < 0.65:
            return 0.1
        if score < 0.75:
            return 0.06
        return 0.0

    def _clamp(self, score):
        return round(max(0.0, min(1.0, score)), 2)
