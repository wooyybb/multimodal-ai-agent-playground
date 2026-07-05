from time import perf_counter

from generation.generation_config import GenerationConfig
from generation.generation_planner import GenerationPlanner
from generation.generation_result import GenerationResult
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

        config = GenerationConfig.from_plan(plan)
        negative_prompt = state.get("provider_negative_prompt") or state.get("negative_prompt") or ""
        started = perf_counter()
        result = provider.generate(
            prompt,
            state,
            fallback_generate=fallback_generate,
            negative_prompt=negative_prompt,
            config=config,
        )
        if isinstance(result, GenerationResult):
            result = result.to_dict()
        latency = round(perf_counter() - started, 4)
        result.setdefault("latency", latency)
        result["generation_plan"] = plan
        result["generation_config"] = config.to_dict()
        result["generation_mode"] = plan.get("generation_mode")
        result["generation_provider"] = provider_name
        result["cfg"] = plan.get("cfg")
        result["steps"] = plan.get("steps")
        result["scheduler"] = plan.get("scheduler")
        result["resolution"] = plan.get("resolution")
        result["future_hooks"] = plan.get("future_hooks", {})
        result["prompt_length"] = len(str(prompt or "").split())
        print(f"[GenerationRouter] Provider: {provider_name}")
        print(f"[GenerationRouter] Mode: {result['generation_mode']}")
        print(f"[GenerationRouter] Resolution: {result.get('resolution')}")
        print(f"[GenerationRouter] Steps: {result.get('steps')}")
        print(f"[GenerationRouter] CFG: {result.get('cfg')}")
        print(f"[GenerationRouter] Latency: {result.get('latency')}s")
        print(f"[GenerationRouter] Output: {result.get('output_image_path')}")
        return result
