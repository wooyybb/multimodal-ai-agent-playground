import json
from pathlib import Path


class ProviderRouter:
    CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "providers.json"

    def run(
        self,
        state_or_user_prompt,
        scene_plan: dict | None = None,
        planner_result: dict | None = None,
        available_providers: list[str] | None = None,
    ) -> dict:
        if isinstance(state_or_user_prompt, dict):
            result = self._run_legacy(
                state_or_user_prompt.get("user_prompt", ""),
                scene_plan=state_or_user_prompt.get("scene_plan"),
                planner_result=state_or_user_prompt.get("planner_result"),
                available_providers=available_providers,
            )
            return {
                "provider_routing": result,
                "provider": result.get("selected_provider", "flux"),
            }

        return self._run_legacy(
            state_or_user_prompt,
            scene_plan=scene_plan,
            planner_result=planner_result,
            available_providers=available_providers,
        )

    def _run_legacy(
        self,
        user_prompt: str,
        scene_plan: dict | None = None,
        planner_result: dict | None = None,
        available_providers: list[str] | None = None,
    ) -> dict:
        print("[ProviderRouter] Running...")
        config = self._load_config()
        providers = config.get("providers", {})
        default_provider = config.get("default_provider", "flux")
        enabled_providers = [
            name for name, info in providers.items() if info.get("enabled") is True
        ]

        if available_providers is not None:
            enabled_providers = [
                provider for provider in enabled_providers if provider in available_providers
            ]
        if not enabled_providers:
            enabled_providers = [default_provider]

        print(f"[ProviderRouter] Enabled providers: {enabled_providers}")
        print(f"[ProviderRouter] Default provider: {default_provider}")

        requested_provider = self._requested_provider(user_prompt)
        fallback_provider = (
            default_provider if default_provider in enabled_providers else enabled_providers[0]
        )

        if requested_provider in enabled_providers:
            selected_provider = requested_provider
            reason = f"{requested_provider} is available and matches the request."
        else:
            selected_provider = fallback_provider
            reason = (
                f"{requested_provider} would be suitable for this request, "
                f"but only {', '.join(enabled_providers)} is currently enabled."
            )

        print(f"[ProviderRouter] Requested provider: {requested_provider}")
        print(f"[ProviderRouter] Selected provider: {selected_provider}")
        print(f"[ProviderRouter] Reason: {reason}")
        return {
            "requested_provider": requested_provider,
            "selected_provider": selected_provider,
            "fallback_provider": fallback_provider,
            "reason": reason,
            "capabilities": providers,
        }

    def _load_config(self):
        print("[ProviderRouter] Loading providers.json...")
        try:
            with self.CONFIG_PATH.open("r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as error:
            print(f"[ProviderRouter] Failed to load provider config: {error}")
            return {
                "default_provider": "flux",
                "providers": {
                    "flux": {
                        "enabled": True,
                        "display_name": "FLUX.1 Schnell",
                        "supports_long_prompt": False,
                        "supports_negative_prompt": False,
                        "supports_image_edit": False,
                        "supports_multi_image": False,
                        "speed": "fast",
                        "quality": "high",
                    }
                },
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
