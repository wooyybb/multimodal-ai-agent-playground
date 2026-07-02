class ExpressionAgent:
    def run(self, user_prompt: str, scene_plan: dict | None = None) -> dict:
        print("[ExpressionAgent] Running...")
        text = str(user_prompt or "").lower()
        scene_plan = scene_plan or {}
        expression_rules = ["soft smile", "natural readable emotions"]
        avoid = ["blank faces", "aggressive reactions", "seductive expressions"]

        emotion = scene_plan.get("emotion", "")
        if "warm" in emotion or "playful" in emotion:
            expression_rules.extend(["playful grin", "laughing face"])
        if "dramatic" in emotion:
            expression_rules = ["focused expression", "intense gaze"]
        if "playful" in text:
            expression_rules.append("playful grin")
        if "laugh" in text or "funny" in text:
            expression_rules.append("laughing face")

        return {
            "expression_rules": expression_rules,
            "avoid": avoid,
        }
