class ScenePlanningAgent:
    def run(
        self,
        user_prompt: str,
        caption: str | None = None,
        planner_result: dict | None = None,
    ) -> dict:
        print("[ScenePlanningAgent] Running...")
        text = f"{user_prompt or ''} {caption or ''}".lower()

        scene_type = self._scene_type(text)
        emotion = self._emotion(text)
        relationship = self._relationship(text)
        plan = {
            "scene_type": scene_type,
            "emotion": emotion,
            "relationship": relationship,
            "interaction": self._interaction(scene_type, relationship),
            "energy": self._energy(scene_type, emotion),
            "narrative": self._narrative(scene_type, relationship),
            "camera_intent": self._camera_intent(scene_type),
            "scene_rules": self._scene_rules(scene_type, emotion),
            "avoid": self._avoid(scene_type),
        }

        print(f"[ScenePlanningAgent] Scene type: {plan['scene_type']}")
        print(f"[ScenePlanningAgent] Emotion: {plan['emotion']}")
        print(f"[ScenePlanningAgent] Relationship: {plan['relationship']}")
        return plan

    def _scene_type(self, text):
        if any(word in text for word in ("인생네컷", "포토이즘", "photobooth")):
            return "photobooth_memory"
        if "프로필" in text or "profile" in text:
            return "profile_portrait"
        if "포스터" in text or "poster" in text:
            return "poster_illustration"
        if "스티커" in text or "sticker" in text:
            return "sticker_sheet"
        if any(word in text for word in ("전투", "battle", "combat")):
            return "action_scene"
        return "illustration_scene"

    def _emotion(self, text):
        if any(word in text for word in ("장난", "playful", "fun")):
            return "playful and cheerful"
        if any(word in text for word in ("감성", "따뜻", "warm")):
            return "warm and soft"
        if "시네마틱" in text or "cinematic" in text:
            return "dramatic but controlled"
        return "natural and readable"

    def _relationship(self, text):
        if any(word in text for word in ("친구", "friends", "같이")):
            return "friends"
        if "커플" in text or "couple" in text:
            return "close pair"
        if "혼자" in text or "solo" in text:
            return "solo subject"
        return "unspecified"

    def _interaction(self, scene_type, relationship):
        if scene_type == "photobooth_memory":
            return "casual posing together"
        if scene_type == "action_scene":
            return "dynamic action movement"
        if relationship == "friends":
            return "friendly interaction"
        if relationship == "close pair":
            return "close side-by-side interaction"
        return "clear subject presentation"

    def _energy(self, scene_type, emotion):
        if scene_type == "action_scene":
            return "high energy and dynamic"
        if "playful" in emotion:
            return "soft, relaxed, candid"
        if "dramatic" in emotion:
            return "controlled and cinematic"
        return "calm and readable"

    def _narrative(self, scene_type, relationship):
        if scene_type == "photobooth_memory":
            return f"{relationship} casually taking photobooth pictures together"
        if scene_type == "profile_portrait":
            return "a clean profile portrait focused on personality"
        if scene_type == "poster_illustration":
            return "a poster-like illustration with clear visual hierarchy"
        if scene_type == "action_scene":
            return "characters captured in a dynamic action moment"
        return "a clear illustration scene with readable character intent"

    def _camera_intent(self, scene_type):
        if scene_type == "photobooth_memory":
            return "eye-level candid snapshot"
        if scene_type == "profile_portrait":
            return "medium close-up portrait"
        if scene_type == "poster_illustration":
            return "center-focused poster framing"
        if scene_type == "action_scene":
            return "dynamic wide camera"
        return "clear eye-level composition"

    def _scene_rules(self, scene_type, emotion):
        rules = ["keep emotional readability high"]
        if scene_type == "photobooth_memory":
            rules.extend([
                "prioritize natural snapshot feeling",
                "avoid dramatic action composition",
            ])
        elif scene_type == "action_scene":
            rules.extend(["emphasize motion", "keep silhouettes readable"])
        elif scene_type == "poster_illustration":
            rules.extend(["strong visual hierarchy", "clean focal point"])
        if "warm" in emotion:
            rules.append("preserve warm gentle mood")
        return rules

    def _avoid(self, scene_type):
        if scene_type == "photobooth_memory":
            return ["combat scene", "fashion showcase", "cinematic poster staging"]
        if scene_type == "action_scene":
            return ["stiff pose", "flat composition"]
        return ["unclear staging", "confusing interaction"]
