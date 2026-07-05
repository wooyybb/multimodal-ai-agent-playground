from generation.generation_result import GenerationResult


class FluxFastProvider:
    name = "flux_fast"

    def generate(
        self,
        prompt: str,
        state: dict,
        fallback_generate,
        negative_prompt: str = "",
        config=None,
    ) -> dict:
        print("[GenerationRouter] Provider: flux_fast")
        output_path = fallback_generate(prompt)
        config_dict = config.to_dict() if config else {}
        return GenerationResult(
            output_image_path=output_path,
            generation_provider=self.name,
            generation_backend="FLUX",
            generation_mode="fast",
            generation_config=config_dict,
            prompt_length=len(str(prompt or "").split()),
            generation_notes=["used existing FLUX generation path"],
        )
