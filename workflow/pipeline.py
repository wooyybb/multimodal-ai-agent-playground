from agents.prompt_agent import PromptAgent
from agents.vision_agent import VisionAgent


class MultimodalPipeline:
    def __init__(self):
        self.vision_agent = VisionAgent()
        self.prompt_agent = PromptAgent()

    def run(self, image, user_prompt):
        print("[Pipeline] Starting pipeline...")
        caption = self.vision_agent.run(image)
        final_prompt = self.prompt_agent.run(caption, user_prompt)
        print("[Pipeline] Finished pipeline.")

        return {
            "caption": caption,
            "final_prompt": final_prompt,
        }
