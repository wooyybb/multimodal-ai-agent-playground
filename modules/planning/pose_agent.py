class PoseAgent:
    def run(
        self,
        user_prompt: str,
        character_section: dict | None = None,
        scene_plan: dict | None = None,
    ) -> dict:
        print("[PoseAgent] Running...")
        text = str(user_prompt or "").lower()
        scene_plan = scene_plan or {}
        pose_rules = ["relaxed posture", "natural hand gestures"]
        avoid = ["combat stance", "dramatic action scene", "seductive pose"]

        if scene_plan.get("relationship") == "friends":
            pose_rules.extend(["casual posing", "shoulder leaning"])
        if "playful" in scene_plan.get("emotion", ""):
            pose_rules.append("peace signs")
        if scene_plan.get("scene_type") == "action_scene":
            pose_rules = ["dynamic pose", "strong silhouette"]
            avoid = ["stiff pose", "unclear action"]
        if "photobooth" in text:
            pose_rules.insert(0, "casual photobooth posing")
        if "peace" in text or "v sign" in text:
            pose_rules.append("peace signs")
        if character_section and "sword" in str(character_section).lower():
            avoid.append("weapon showcase")

        return {"pose_rules": pose_rules, "avoid": avoid}
