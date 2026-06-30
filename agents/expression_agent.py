class ExpressionAgent:
    def run(self, user_prompt: str) -> dict:
        print("[ExpressionAgent] Running...")
        text = str(user_prompt or "").lower()
        expression_rules = ["soft smile", "natural readable emotions"]
        avoid = ["blank faces", "aggressive reactions", "seductive expressions"]

        if "playful" in text:
            expression_rules.append("playful grin")
        if "laugh" in text or "funny" in text:
            expression_rules.append("laughing face")

        return {
            "expression_rules": expression_rules,
            "avoid": avoid,
        }
