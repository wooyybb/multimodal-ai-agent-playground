class FluxFastProvider:
    name = "flux_fast"

    def generate(self, prompt: str, state: dict, fallback_generate) -> dict:
        print("[GenerationRouter] Provider: flux_fast")
        output_path = fallback_generate(prompt)
        return {
            "output_image_path": output_path,
            "generation_provider": self.name,
            "generation_backend": "FLUX",
            "generation_mode": "fast",
            "generation_notes": ["used existing FLUX generation path"],
        }
