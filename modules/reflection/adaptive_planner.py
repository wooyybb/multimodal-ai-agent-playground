class AdaptivePlanner:
    def run(self, state: dict) -> dict:
        print("[AdaptivePlanner] Running...")
        state = state or {}
        score = float(state.get("score") or 0.0)
        reflection = str(state.get("reflection") or "")
        prompt = str(state.get("final_prompt") or "")
        caption = str(state.get("caption") or "")
        text = f"{reflection} {prompt} {caption}".lower()

        failure_analysis = self._failure_analysis(score, text)
        hypothesis = self._hypothesis(score, text)
        selected_strategy = state.get("selected_strategy") or {}
        strategy = selected_strategy.get("title") or self._strategy(score, text)
        context_updates = self._context_updates(score, text, selected_strategy)
        priority_change = self._priority_change(score, text, selected_strategy)
        confidence = self._confidence(score, context_updates)

        print(f"[AdaptivePlanner] Failure: {failure_analysis}")
        print(f"[AdaptivePlanner] Strategy: {strategy}")

        return {
            "adaptive_plan": {
                "failure_analysis": failure_analysis,
                "hypothesis": hypothesis,
                "strategy": strategy,
                "selected_strategy": selected_strategy,
                "context_updates": context_updates,
                "priority_change": priority_change,
                "confidence": confidence,
            }
        }

    def _failure_analysis(self, score, text):
        if score >= 0.75:
            return "Score meets retry threshold; no major adaptive failure detected."
        if "layout" in text or "composition" in text:
            return "Low score may come from weak composition or layout mismatch."
        if "style" in text and "conflict" in text:
            return "Low score may come from style conflict."
        if "character" in text or "subject" in text or "caption" in text:
            return "Low score may come from weak subject identity preservation."
        if score < 0.70:
            return "Low CLIP score suggests prompt-image alignment is weak."
        return "Score is below target; improve visual alignment before retry."

    def _hypothesis(self, score, text):
        if score >= 0.75:
            return "Current plan is likely sufficient."
        if "layout" in text or "composition" in text:
            return "Simplifying camera and composition should improve alignment."
        if "style" in text and "conflict" in text:
            return "Reducing style priority should make the subject easier to match."
        if "character" in text or "subject" in text or "caption" in text:
            return "Increasing character identity priority should improve similarity."
        return "A more focused subject-first prompt should improve retry output."

    def _strategy(self, score, text):
        if score >= 0.75:
            return "Keep current generation strategy."
        strategies = []
        if score < 0.70:
            strategies.extend(
                [
                    "increase character priority",
                    "simplify layout",
                    "reduce decorative style weight",
                ]
            )
        if "layout" in text or "composition" in text:
            strategies.append("use clearer camera framing")
        if "style" in text and "conflict" in text:
            strategies.append("preserve only essential style keywords")
        if not strategies:
            strategies.append("focus retry prompt on subject, composition, and caption fidelity")
        return "; ".join(dict.fromkeys(strategies))

    def _context_updates(self, score, text, selected_strategy=None):
        updates = []
        selected_strategy = selected_strategy or {}
        strategy_id = selected_strategy.get("id")
        if score < 0.70:
            updates.extend(
                [
                    "strengthen recognizable subject identity",
                    "simplify layout with clear centered composition",
                    "reduce decorative style details",
                ]
            )
        if "character" in text or "subject" in text or "caption" in text:
            updates.append("preserve caption-specific subject details")
        if "layout" in text or "composition" in text:
            updates.append("use eye-level camera and balanced framing")
        if "style" in text and "conflict" in text:
            updates.append("keep style secondary to subject clarity")
        if strategy_id == "S1":
            updates.append("increase preserve prompt for identity details")
        elif strategy_id == "S2":
            updates.append("change camera to clearer centered framing")
        elif strategy_id == "S3":
            updates.append("strengthen coherent lighting and reduce harsh contrast")
        elif strategy_id == "S4":
            updates.append("reduce style weight while keeping requested style visible")
        if not updates and score < 0.75:
            updates.append("improve prompt-image alignment with clearer visual hierarchy")
        return list(dict.fromkeys(updates))

    def _priority_change(self, score, text, selected_strategy=None):
        changes = []
        selected_strategy = selected_strategy or {}
        strategy_id = selected_strategy.get("id")
        if score < 0.70:
            changes.extend(["character +2", "layout +1", "style -1"])
        if "character" in text or "subject" in text or "caption" in text:
            changes.append("identity +2")
        if "layout" in text or "composition" in text:
            changes.append("camera +1")
        if "style" in text and "conflict" in text:
            changes.append("style -2")
        if strategy_id == "S1":
            changes.extend(["identity +2", "style -1"])
        elif strategy_id == "S2":
            changes.extend(["composition +2", "camera +1"])
        elif strategy_id == "S3":
            changes.extend(["lighting +2", "contrast -1"])
        elif strategy_id == "S4":
            changes.extend(["style -1", "identity +1"])
        if not changes and score < 0.75:
            changes.append("alignment +1")
        return list(dict.fromkeys(changes))

    def _confidence(self, score, context_updates):
        if score >= 0.75:
            return 0.55
        if score < 0.70 and context_updates:
            return 0.91
        return 0.78
