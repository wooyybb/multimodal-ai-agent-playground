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
        print("[OrchestratorAgent] Initial attempt started.")
        output_image_path = self.generation_agent.run(final_prompt)
        score = self.evaluation_agent.run(image, output_image_path, final_prompt)
        reflection_result = self.reflection_agent.run(caption, final_prompt, score)
        retry_needed = self.retry_agent.should_retry(score)

        retry_output_image_path = None
        retry_score = None

        if retry_needed:
            print("[OrchestratorAgent] Retry needed. Starting second attempt.")
            retry_output_image_path = self.generation_agent.run(
                reflection_result["suggested_prompt"]
            )
            retry_score = self.evaluation_agent.run(
                image,
                retry_output_image_path,
                reflection_result["suggested_prompt"],
            )
        else:
            print("[OrchestratorAgent] Retry skipped.")

        if retry_score is not None and retry_score > score:
            best_prompt = reflection_result["suggested_prompt"]
            best_output_image_path = retry_output_image_path
            best_score = retry_score
        else:
            best_prompt = final_prompt
            best_output_image_path = output_image_path
            best_score = score

        print(f"[OrchestratorAgent] Best score selected: {best_score}")
        memory_saved = False
        history_path = None
        try:
            history_path = self.memory_manager.save_run(
                {
                    "caption": caption,
                    "initial_prompt": final_prompt,
                    "initial_score": score,
                    "initial_output_image_path": output_image_path,
                    "reflection": reflection_result["reflection"],
                    "retry_needed": retry_needed,
                    "retry_prompt": (
                        reflection_result["suggested_prompt"]
                        if retry_needed
                        else None
                    ),
                    "retry_score": retry_score,
                    "retry_output_image_path": retry_output_image_path,
                    "best_prompt": best_prompt,
                    "best_score": best_score,
                    "best_output_image_path": best_output_image_path,
                }
            )
            memory_saved = True
        except Exception as error:
            print(f"[Memory] Save failed: {error}")

        print("[OrchestratorAgent] Multi-agent workflow finished.")
        return {
            "caption": caption,
            "final_prompt": final_prompt,
            "output_image_path": output_image_path,
            "score": score,
            "retry_needed": retry_needed,
            "retry_output_image_path": retry_output_image_path,
            "retry_score": retry_score,
            "reflection": reflection_result["reflection"],
            "suggested_prompt": reflection_result["suggested_prompt"],
            "best_prompt": best_prompt,
            "best_output_image_path": best_output_image_path,
            "best_score": best_score,
            "history_path": history_path,
            "last_run": last_run,
            "memory_saved": memory_saved,
            "agent_trace": [
                "MemoryManager loaded last run",
                "VisionAgent generated caption",
                "PromptAgent generated final prompt",
                "GenerationAgent generated mock image",
                "EvaluationAgent generated mock score",
                "ReflectionAgent generated reflection",
                "RetryAgent decided retry status",
                "OrchestratorAgent selected best result",
                (
                    "MemoryManager saved run history"
                    if memory_saved
                    else "MemoryManager save skipped after error"
                ),
            ],
        }
