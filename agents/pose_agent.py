class PoseAgent:
    def run(self, user_prompt: str, character_section: dict | None = None) -> dict:
        print("[PoseAgent] Running...")
        text = str(user_prompt or "").lower()
        pose_rules = ["relaxed posture", "natural hand gestures"]
        avoid = ["combat stance", "dramatic action scene", "seductive pose"]

        if "photobooth" in text:
            pose_rules.insert(0, "casual photobooth posing")
        if "peace" in text or "v sign" in text:
            pose_rules.append("peace signs")
        if character_section and "sword" in str(character_section).lower():
            avoid.append("weapon showcase")

        return {"pose_rules": pose_rules, "avoid": avoid}
