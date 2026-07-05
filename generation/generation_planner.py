import os


class GenerationPlanner:
    FAST_PRESET = {
        "generation_mode": "fast",
        "provider": "flux_fast",
        "cfg": None,
        "steps": 4,
        "resolution": "1024x1024",
        "scheduler": "schnell",
        "future_hooks": {
            "ip_adapter": "planned",
            "controlnet": "planned",
        },
    }
    QUALITY_PRESET = {
        "generation_mode": "quality",
        "provider": "sdxl_quality",
        "cfg": 7.5,
        "steps": 30,
        "resolution": "1024x1024",
        "scheduler": "DPM++ 2M Karras",
        "future_hooks": {
            "ip_adapter": "planned",
            "controlnet": "planned",
        },
    }

    def plan(self, state: dict) -> dict:
        print("[GenerationPlanner] Planning generation preset...")
        mode = self._mode(state)
        preset = dict(self.QUALITY_PRESET if mode == "quality" else self.FAST_PRESET)
        preset["reason"] = self._reason(state, mode)
        print(f"[GenerationPlanner] Mode: {preset['generation_mode']}")
        print(f"[GenerationPlanner] Provider: {preset['provider']}")
        print(f"[GenerationPlanner] Steps: {preset['steps']}")
        return preset

    def _mode(self, state):
        provider_override = self._provider_override()
        if provider_override == "sdxl_quality":
            return "quality"
        if provider_override == "flux_fast":
            return "fast"

        explicit = str(state.get("generation_mode") or "").lower()
        requested = str(state.get("requested_provider") or state.get("provider") or "").lower()
        user_prompt = str(state.get("user_prompt") or "").lower()
        text = " ".join([explicit, requested, user_prompt])
        if any(keyword in text for keyword in ("quality", "sdxl", "identity", "preserve", "high fidelity")):
            return "quality"
        return "fast"

    def _provider_override(self):
        provider = str(os.getenv("GENERATION_PROVIDER") or "").strip().lower()
        if provider in {"flux_fast", "sdxl_quality"}:
            return provider
        return ""

    def _reason(self, state, mode):
        if mode == "quality":
            return (
                "Quality mode selected for stronger identity, outfit, accessory, "
                "and visual detail preservation."
            )
        return "Fast mode selected for lightweight FLUX generation."
