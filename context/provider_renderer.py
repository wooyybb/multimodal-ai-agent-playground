from context.provider_prompt_compiler import ProviderPromptCompiler


class ProviderRenderer:
    def __init__(self):
        self.compiler = ProviderPromptCompiler()

    def render(
        self,
        program: dict,
        provider: str = "flux",
        forbidden_concepts=None,
        negative_prompt=None,
    ) -> dict:
        return self.compiler.compile(
            program,
            provider=provider,
            forbidden_concepts=forbidden_concepts,
            negative_prompt=negative_prompt,
        )

    def render_flux(self, program):
        return self.render(program, provider="flux")["flux_prompt"]

    def render_sdxl(self, program):
        return self.render(program, provider="sdxl_quality")["sdxl_style_prompt"]

    def render_clip(self, program):
        return self.render(program, provider="clip_eval")["clip_prompt"]

    def render_pickscore(self, program):
        return self.render(program, provider="pickscore")["pickscore_prompt"]

    def render_vlm_judge(self, program):
        return self.render(program, provider="vlm_judge")["vlm_judge_prompt"]

    def render_negative(self, program):
        return self.render(program, provider="negative")["negative_prompt"]
