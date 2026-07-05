from generation.generation_planner import GenerationPlanner
from provider.flux_fast_provider import FluxFastProvider
from provider.sdxl_quality_provider import SDXLQualityProvider


class GenerationRouter:
    def __init__(self, planner=None, providers=None):
        self.planner = planner or GenerationPlanner()
        self.providers = providers or {
            "flux_fast": FluxFastProvider(),
            "sdxl_quality": SDXLQualityProvider(),
        }

    def generate(self, state: dict, fallback_generate) -> dict:
        print("[GenerationRouter] Routing generation request...")
        plan = self.planner.plan(state)
        provider_name = plan.get("provider", "flux_fast")
        provider = self.providers.get(provider_name)
        if provider is None:
            print("[GenerationRouter] Unknown provider. Falling back to flux_fast.")
            provider_name = "flux_fast"
            provider = self.providers[provider_name]
            plan["provider"] = provider_name
            plan["generation_mode"] = "fast"
            plan["reason"] = "unknown provider fallback to flux_fast"

        prompt = state.get("generation_prompt") or state.get("final_prompt") or ""
        state["generation_plan"] = plan
        state["generation_mode"] = plan.get("generation_mode")
        state["generation_provider"] = provider_name

        result = provider.generate(prompt, state, fallback_generate)
        result["generation_plan"] = plan
        result["generation_mode"] = plan.get("generation_mode")
        result["generation_provider"] = provider_name
        result["cfg"] = plan.get("cfg")
        result["steps"] = plan.get("steps")
        result["scheduler"] = plan.get("scheduler")
        result["resolution"] = plan.get("resolution")
        result["future_hooks"] = plan.get("future_hooks", {})
        print(f"[GenerationRouter] Mode: {result['generation_mode']}")
        print(f"[GenerationRouter] Output: {result.get('output_image_path')}")
        return result
