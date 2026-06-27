from agents.prompt_agent import PromptAgent
from agents.vision_agent import VisionAgent


class OrchestratorAgent:
    def __init__(self):
        self.vision_agent = VisionAgent()
        self.prompt_agent = PromptAgent()

    def run(self, image, user_prompt):
        print("[OrchestratorAgent] Starting multi-agent workflow...")

        caption = self.vision_agent.run(image)
        final_prompt = self.prompt_agent.run(caption, user_prompt)

        print("[OrchestratorAgent] Multi-agent workflow finished.")
        return {
            "caption": caption,
            "final_prompt": final_prompt,
            "agent_trace": [
                "VisionAgent generated caption",
                "PromptAgent generated final prompt",
            ],
        }
