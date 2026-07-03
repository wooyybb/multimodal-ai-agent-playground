class LLMContextReasoner:
    def run(self, state: dict) -> dict:
        print("[LLMContextReasoner] Running...")
        state = state or {}
        user_prompt = str(state.get("user_prompt") or "").strip()
        caption = str(state.get("caption") or "").strip()
        text = f"{caption} {user_prompt}".strip()
        lower_text = text.lower()

        reasoning = {
            "user_goal": self._user_goal(user_prompt, caption),
            "scene_goal": self._scene_goal(lower_text),
            "composition_goal": self._composition_goal(lower_text),
            "interaction_goal": self._interaction_goal(lower_text),
            "style_goal": self._style_goal(lower_text),
            "priority": self._priority(lower_text),
            "mode": "mock_llm_rule_based",
        }

        print(f"[LLMContextReasoner] User Goal: {reasoning['user_goal']}")
        print(f"[LLMContextReasoner] Scene Goal: {reasoning['scene_goal']}")
        return {"context_reasoning": reasoning}

    def _user_goal(self, user_prompt, caption):
        if user_prompt and caption:
            return f"Transform the image subject into: {user_prompt}"
        if user_prompt:
            return f"Generate an image matching: {user_prompt}"
        if caption:
            return f"Generate an image based on: {caption}"
        return "Generate a clear image from the available context"

    def _scene_goal(self, text):
        if "photobooth" in text:
            return "create a photobooth memory scene"
        if "portrait" in text:
            return "create a focused character portrait"
        if "cinematic" in text:
            return "create a cinematic visual scene"
        if "group" in text or "friends" in text or "couple" in text:
            return "show relationship and shared moment clearly"
        return "create a coherent visual scene"

    def _composition_goal(self, text):
        if "photobooth" in text:
            return "use connected vertical frames with consistent camera distance"
        if "poster" in text:
            return "use strong center hierarchy and clean negative space"
        if "close" in text or "portrait" in text:
            return "use close or medium framing focused on the subject"
        return "use balanced composition with readable subject placement"

    def _interaction_goal(self, text):
        if "friends" in text:
            return "show friendly interaction and warm emotional connection"
        if "couple" in text:
            return "show gentle romantic connection without clutter"
        if "group" in text:
            return "keep each person visually separated and recognizable"
        return "keep the main subject expression and pose easy to read"

    def _style_goal(self, text):
        if "anime" in text:
            return "prioritize anime style with clean line art"
        if "webtoon" in text:
            return "prioritize soft webtoon rendering"
        if "realistic" in text:
            return "prioritize realistic lighting and texture"
        if "cinematic" in text:
            return "prioritize cinematic mood and lighting"
        return "prioritize high quality, coherent visual style"

    def _priority(self, text):
        priority = []
        if any(word in text for word in ("girl", "boy", "character", "person", "friends", "couple")):
            priority.append("character")
        if any(word in text for word in ("emotion", "smile", "warm", "cute", "romantic")):
            priority.append("emotion")
        if any(word in text for word in ("photobooth", "poster", "portrait", "layout", "frame")):
            priority.append("layout")
        if any(word in text for word in ("anime", "webtoon", "cinematic", "realistic", "style")):
            priority.append("style")

        for fallback in ("character", "emotion", "layout", "style"):
            if fallback not in priority:
                priority.append(fallback)
        return priority[:4]
