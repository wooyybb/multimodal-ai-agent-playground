class ProviderRouter:
    CAPABILITIES = {
        "flux": ["text_to_image", "fast_generation"],
        "sdxl": ["text_to_image", "negative_prompt", "style_control"],
        "gpt_image": ["long_instruction_following", "image_editing"],
        "imagen": ["natural_language_prompting"],
    }

    def run(
        self,
        user_prompt: str,
        scene_plan: dict | None = None,
        planner_result: dict | None = None,
        available_providers: list[str] | None = None,
    ) -> dict:
        print("[ProviderRouter] Running...")
        available_providers = available_providers or ["flux"]
        requested_provider = self._requested_provider(user_prompt)
        fallback_provider = "flux"

        if requested_provider in available_providers:
            selected_provider = requested_provider
            reason = f"{requested_provider} is available and matches the request."
        else:
            selected_provider = fallback_provider
            reason = (
                f"{requested_provider} would be suitable for this request, "
                f"but only {', '.join(available_providers)} is currently available."
            )

        print(f"[ProviderRouter] Requested provider: {requested_provider}")
        print(f"[ProviderRouter] Selected provider: {selected_provider}")
        print(f"[ProviderRouter] Reason: {reason}")
        return {
            "requested_provider": requested_provider,
            "selected_provider": selected_provider,
            "fallback_provider": fallback_provider,
            "reason": reason,
            "capabilities": self.CAPABILITIES,
        }

    def _requested_provider(self, user_prompt):
        text = str(user_prompt or "").lower()
        if any(
            keyword in text
            for keyword in (
                "\uae34 \ud504\ub86c\ud504\ud2b8",
                "detailed instruction",
                "complex instruction",
                "edit",
                "\uc218\uc815",
            )
        ):
            return "gpt_image"
        if any(
            keyword in text
            for keyword in ("negative prompt", "controlnet", "local", "style control")
        ):
            return "sdxl"
        if any(
            keyword in text
            for keyword in ("\ube60\ub974\uac8c", "fast", "schnell", "quick")
        ):
            return "flux"
        return "flux"
