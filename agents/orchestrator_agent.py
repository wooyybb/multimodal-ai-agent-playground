from agents.evaluation_agent import EvaluationAgent
from agents.generation_agent import GenerationAgent
from agents.prompt_agent import PromptAgent
from agents.reflection_agent import ReflectionAgent
from agents.retry_agent import RetryAgent
from agents.vision_agent import VisionAgent


class OrchestratorAgent:
    def __init__(self):
        self.vision_agent = VisionAgent()
        self.prompt_agent = PromptAgent()
        self.generation_agent = GenerationAgent()
        self.evaluation_agent = EvaluationAgent()
        self.retry_agent = RetryAgent()
        self.reflection_agent = ReflectionAgent()

    def run(self, image, user_prompt):
        print("[OrchestratorAgent] Starting multi-agent workflow...")

        caption = self.vision_agent.run(image)
        final_prompt = self.prompt_agent.run(caption, user_prompt)
        output_image_path = self.generation_agent.run(final_prompt)
        score = self.evaluation_agent.run(image, output_image_path, final_prompt)
        retry_needed = self.retry_agent.should_retry(score)
        reflection_result = self.reflection_agent.run(caption, final_prompt, score)

        print("[OrchestratorAgent] Multi-agent workflow finished.")
        return {
            "caption": caption,
            "final_prompt": final_prompt,
            "output_image_path": output_image_path,
            "score": score,
            "retry_needed": retry_needed,
            "reflection": reflection_result["reflection"],
            "suggested_prompt": reflection_result["suggested_prompt"],
            "agent_trace": [
                "VisionAgent generated caption",
                "PromptAgent generated final prompt",
                "GenerationAgent generated mock image",
                "EvaluationAgent generated mock score",
                "RetryAgent decided retry status",
                "ReflectionAgent generated reflection",
            ],
        }
