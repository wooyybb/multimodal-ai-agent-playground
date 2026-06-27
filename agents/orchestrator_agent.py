from agents.evaluation_agent import EvaluationAgent
from agents.generation_agent import GenerationAgent
from agents.prompt_agent import PromptAgent
from agents.reflection_agent import ReflectionAgent
from agents.retry_agent import RetryAgent
from agents.vision_agent import VisionAgent
from memory.history import MemoryManager


class OrchestratorAgent:
    def __init__(self):
        self.vision_agent = VisionAgent()
        self.prompt_agent = PromptAgent()
        self.generation_agent = GenerationAgent()
        self.evaluation_agent = EvaluationAgent()
        self.reflection_agent = ReflectionAgent()
        self.retry_agent = RetryAgent()
        self.memory_manager = MemoryManager()

    def run(self, image, user_prompt):
        print("[OrchestratorAgent] Starting multi-agent workflow...")
        last_run = self.memory_manager.load_last_run()

        caption = self.vision_agent.run(image)
        final_prompt = self.prompt_agent.run(caption, user_prompt)
        output_image_path = self.generation_agent.run(final_prompt)
        score = self.evaluation_agent.run(image, output_image_path, final_prompt)
        reflection_result = self.reflection_agent.run(caption, final_prompt, score)
        retry_needed = self.retry_agent.should_retry(score)
        history_path = self.memory_manager.save_run(
            {
                "caption": caption,
                "prompt": final_prompt,
                "score": score,
                "reflection": reflection_result["reflection"],
                "retry": retry_needed,
                "output_image_path": output_image_path,
            }
        )

        print("[OrchestratorAgent] Multi-agent workflow finished.")
        return {
            "caption": caption,
            "final_prompt": final_prompt,
            "output_image_path": output_image_path,
            "score": score,
            "retry_needed": retry_needed,
            "reflection": reflection_result["reflection"],
            "suggested_prompt": reflection_result["suggested_prompt"],
            "history_path": history_path,
            "last_run": last_run,
            "memory_saved": True,
            "agent_trace": [
                "MemoryManager loaded last run",
                "VisionAgent generated caption",
                "PromptAgent generated final prompt",
                "GenerationAgent generated mock image",
                "EvaluationAgent generated mock score",
                "ReflectionAgent generated reflection",
                "RetryAgent decided retry status",
                "MemoryManager saved run history",
            ],
        }
