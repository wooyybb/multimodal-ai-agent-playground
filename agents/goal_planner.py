class GoalPlanner:
    def run(self, state: dict) -> dict:
        print("[GoalPlanner] Running...")
        state = state or {}
        user_prompt = str(state.get("user_prompt") or "")
        caption = str(state.get("caption") or "")
        text = f"{user_prompt} {caption}".lower()

        priorities = self._priorities(text)
        goal_tree = {
            "main_goal": self._main_goal(user_prompt, caption),
            "sub_goals": self._sub_goals(text),
            "priorities": priorities,
            "success_criteria": self._success_criteria(text, priorities),
        }

        print(f"[GoalPlanner] Main Goal: {goal_tree['main_goal']}")
        print(f"[GoalPlanner] Priorities: {priorities}")
        return {"goal_tree": goal_tree}

    def _main_goal(self, user_prompt, caption):
        if user_prompt and caption:
            return "Generate an image that preserves the reference identity while following the user request."
        if user_prompt:
            return "Generate an image that follows the user request."
        if caption:
            return "Generate an image faithful to the visual reference."
        return "Generate a coherent high-quality image."

    def _sub_goals(self, text):
        goals = ["preserve subject identity", "maintain clear composition"]
        if "anime" in text or "webtoon" in text:
            goals.append("apply requested illustration style")
        if "cinematic" in text or "lighting" in text:
            goals.append("emphasize lighting and mood")
        if "portrait" in text or "face" in text:
            goals.append("keep face and expression readable")
        if "background" in text or "scene" in text:
            goals.append("keep background consistent with scene intent")
        return list(dict.fromkeys(goals))

    def _priorities(self, text):
        priorities = {
            "identity": 0.8,
            "style": 0.7,
            "composition": 0.7,
            "lighting": 0.6,
            "background": 0.5,
        }
        if "anime" in text or "character" in text:
            priorities["identity"] = 1.0
            priorities["style"] = max(priorities["style"], 0.9)
        if "cinematic" in text or "lighting" in text:
            priorities["lighting"] = 0.9
            priorities["composition"] = max(priorities["composition"], 0.8)
        if "portrait" in text or "face" in text:
            priorities["identity"] = 1.0
            priorities["composition"] = max(priorities["composition"], 0.85)
        if "background" in text or "landscape" in text:
            priorities["background"] = 0.8
        return priorities

    def _success_criteria(self, text, priorities):
        criteria = [
            "generated image matches the user request",
            "main subject remains recognizable",
            "composition is clear and readable",
        ]
        if priorities.get("style", 0) >= 0.9:
            criteria.append("requested style is visible without overriding identity")
        if priorities.get("lighting", 0) >= 0.9:
            criteria.append("lighting mood is visible and coherent")
        if "portrait" in text or "face" in text:
            criteria.append("face and expression are clear")
        return criteria
