from tools.flux_tool import FluxTool


class GenerationAgent:
    def __init__(self, flux_tool=None):
        self.flux_tool = flux_tool or FluxTool()

    def run(self, final_prompt: str) -> str:
        print("[GenerationAgent] Running...")
        output_image_path = self.flux_tool.generate(final_prompt)
        print(f"[GenerationAgent] Output saved: {output_image_path}")
        return output_image_path
