from time import perf_counter

from generation.generation_config import GenerationConfig
from generation.generation_planner import GenerationPlanner
from generation.prompt_renderer import ProviderPromptRenderer
from generation.generation_result import GenerationResult
from generation.style_preset_manager import StylePresetManager
from provider.flux_fast_provider import FluxFastProvider
from provider.sdxl_quality_provider import SDXLQualityProvider


class GenerationRouter:
    def __init__(self, planner=None, providers=None):
        self.planner = planner or GenerationPlanner()
        self.prompt_renderer = ProviderPromptRenderer()
        self.style_preset_manager = StylePresetManager()
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
        if provider_name == "sdxl_quality":
            generation_preset = self.style_preset_manager.select(state)
            plan = self._apply_generation_preset(plan, generation_preset)
            state["generation_preset"] = generation_preset
            state["preset_reason"] = generation_preset.get("reason", "")
            state["environment_overrides"] = generation_preset.get(
                "environment_overrides",
                {},
            )
        else:
            generation_preset = {}

        dense_prompt = state.get("generation_prompt") or state.get("final_prompt") or ""
        state["generation_plan"] = plan
        state["generation_mode"] = plan.get("generation_mode")
        state["generation_provider"] = provider_name
        rendered_prompt = self.prompt_renderer.render(provider_name, dense_prompt, state, plan)
        prompt = rendered_prompt.get("provider_prompt", dense_prompt)
        state["dense_generation_prompt"] = dense_prompt
        state["generation_prompt"] = prompt
        state["provider_prompt_type"] = rendered_prompt.get("prompt_type")
        state["style_prompt"] = rendered_prompt.get("style_prompt", "")
        state["style_prompt_word_count"] = rendered_prompt.get("word_count")
        state["style_prompt_token_count"] = rendered_prompt.get("token_count")
        state["provider_prompt_rendering"] = rendered_prompt
        print(f"[GenerationRouter] Prompt Type: {rendered_prompt.get('prompt_type')}")
        print(f"[GenerationRouter] Prompt Length: {rendered_prompt.get('token_count')} tokens")

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
        provider_generation_config = result.get("generation_config") or {}
        result["generation_plan"] = plan
        result["generation_config"] = {
            **config.to_dict(),
            **provider_generation_config,
        }
        if generation_preset:
            result["generation_preset"] = generation_preset
            result["preset_reason"] = generation_preset.get("reason", "")
            result["environment_overrides"] = generation_preset.get(
                "environment_overrides",
                {},
            )
        result["generation_mode"] = plan.get("generation_mode")
        result["generation_provider"] = provider_name
        result["dense_generation_prompt"] = dense_prompt
        result["generation_prompt"] = prompt
        result["provider_prompt_type"] = rendered_prompt.get("prompt_type")
        result["style_prompt"] = rendered_prompt.get("style_prompt", "")
        result["style_prompt_word_count"] = rendered_prompt.get("word_count")
        result["style_prompt_token_count"] = rendered_prompt.get("token_count")
        result["provider_prompt_rendering"] = rendered_prompt
        result["cfg"] = plan.get("cfg")
        result["strength"] = plan.get("strength") if plan.get("strength") is not None else config.strength
        result["steps"] = plan.get("steps")
        result["scheduler"] = plan.get("scheduler")
        result["resolution"] = plan.get("resolution")
        result["future_hooks"] = plan.get("future_hooks", {})
        result["prompt_length"] = len(str(prompt or "").split())
        result.setdefault("reference_conditioning_enabled", False)
        result.setdefault("conditioning_type", "none")
        result.setdefault("ip_adapter_enabled", False)
        result.setdefault("ip_adapter_loaded", False)
        result.setdefault("ip_adapter_repo_id", "")
        result.setdefault("ip_adapter_subfolder", "")
        result.setdefault("ip_adapter_weight_name", "")
        result.setdefault("ip_adapter_scale", 0.75)
        result.setdefault("used_conditioning_fallback", False)
        result.setdefault("conditioning_fallback_reason", "")
        result.setdefault("conditioning_reason", "")
        result.setdefault("ip_adapter_status", {})
        result.setdefault("style_program", plan.get("style_program", {}))
        result.setdefault("selected_lora", plan.get("selected_lora") or "")
        result.setdefault("lora_status", {})
        result.setdefault("controlnet_status", {})
        controlnet_status = result.get("controlnet_status") or {}
        result.setdefault("controlnet_enabled", bool(controlnet_status.get("enabled")))
        result.setdefault("controlnet_loaded", bool(controlnet_status.get("loaded")))
        result.setdefault("controlnet_type", controlnet_status.get("type", ""))
        result.setdefault("controlnet_scale", controlnet_status.get("scale"))
        result.setdefault("control_image_path", controlnet_status.get("control_image_path", ""))
        result.setdefault(
            "controlnet_fallback_reason",
            controlnet_status.get("fallback_reason", ""),
        )
        result.setdefault("generation_is_mock", False)
        result.setdefault("fallback_reason", "")
        result.setdefault("reference_analysis", {})
        result.setdefault("conditioning_summary", {})
        result.setdefault("conditioned_reference_path", "")
        result.setdefault("conditioning_package", {})
        result.setdefault("generation_error_type", "")
        result.setdefault("generation_error_repr", "")
        result.setdefault("generation_error_traceback", "")
        result.setdefault("generation_error_stage", "")
        result.setdefault("model_id", "")
        result.setdefault("device", "")
        result.setdefault("dtype", "")
        if result.get("strength") is None:
            result["strength"] = config.strength
        print(f"[GenerationRouter] Provider: {provider_name}")
        print(f"[GenerationRouter] Mode: {result['generation_mode']}")
        print(f"[GenerationRouter] Resolution: {result.get('resolution')}")
        print(f"[GenerationRouter] Steps: {result.get('steps')}")
        print(f"[GenerationRouter] CFG: {result.get('cfg')}")
        print(f"[GenerationRouter] Strength: {result.get('strength')}")
        if result.get("device"):
            print(f"[GenerationRouter] Device: {result.get('device')}")
        if result.get("dtype"):
            print(f"[GenerationRouter] Dtype: {result.get('dtype')}")
        print(f"[GenerationRouter] IP-Adapter enabled: {result.get('ip_adapter_enabled')}")
        print(f"[GenerationRouter] IP-Adapter loaded: {result.get('ip_adapter_loaded')}")
        print(f"[GenerationRouter] Latency: {result.get('latency')}s")
        if result.get("fallback_reason"):
            print(f"[GenerationRouter] Fallback reason: {result.get('fallback_reason')}")
        if result.get("generation_error_type"):
            print(
                "[GenerationRouter] Generation error: "
                f"{result.get('generation_error_type')} "
                f"{result.get('generation_error_repr')}"
            )
        print(f"[GenerationRouter] Mock generation: {result.get('generation_is_mock')}")
        print(f"[GenerationRouter] Output: {result.get('output_image_path')}")
        return result

    def _apply_generation_preset(self, plan, preset):
        plan = dict(plan or {})
        if not preset:
            return plan
        plan["strength"] = preset.get("sdxl_strength")
        plan["cfg"] = preset.get("cfg")
        plan["steps"] = preset.get("steps")
        plan["resolution"] = preset.get("resolution")
        plan["generation_preset"] = preset
        plan["preset_reason"] = preset.get("reason", "")
        plan["environment_overrides"] = preset.get("environment_overrides", {})
        return plan
