from agents.evaluation_agent import EvaluationAgent
from agents.generation_agent import GenerationAgent
from agents.planner_agent import PlannerAgent
from agents.prompt_agent import PromptAgent
from agents.reflection_agent import ReflectionAgent
from agents.retry_agent import RetryAgent
from agents.vision_agent import VisionAgent
from memory.history import MemoryManager
from registry import ToolRegistry


class OrchestratorAgent:
    def __init__(self):
        self.planner_agent = PlannerAgent()
        self.vision_agent = VisionAgent()
        self.prompt_agent = PromptAgent()
        self.generation_agent = GenerationAgent()
        self.evaluation_agent = EvaluationAgent()
        self.reflection_agent = ReflectionAgent()
        self.retry_agent = RetryAgent()
        self.memory_manager = MemoryManager()
        self.registry = ToolRegistry()
        self._register_tools()

    def _register_tools(self):
        self.registry.register("memory_load", self.memory_manager.load_last_run)
        self.registry.register("vision", self.vision_agent)
        self.registry.register("prompt", self.prompt_agent)
        self.registry.register("generation", self.generation_agent)
        self.registry.register("evaluation", self.evaluation_agent)
        self.registry.register("reflection", self.reflection_agent)
        self.registry.register("retry", self.retry_agent.should_retry)
        self.registry.register("memory_save", self.memory_manager.save_run)

    def run(self, image, user_prompt):
        print("[OrchestratorAgent] Starting multi-agent workflow...")
        planner_result = self.planner_agent.run(
            user_prompt=user_prompt,
            image_provided=image is not None,
        )
        last_run = self.registry.call("memory_load")

        caption = self.registry.call("vision", image)
        context = {
            "planner_result": planner_result,
            "last_run": last_run,
            "retry_history": [],
            "style_preferences": None,
            "previous_best_prompt": (
                last_run.get("best_prompt") if isinstance(last_run, dict) else None
            ),
            "previous_best_score": (
                last_run.get("best_score") if isinstance(last_run, dict) else None
            ),
        }
        final_prompt = self.registry.call(
            "prompt",
            caption,
            user_prompt,
            context=context,
        )
        print("[OrchestratorAgent] Initial attempt started.")
        output_image_path = self.registry.call("generation", final_prompt)
        score = self.registry.call("evaluation", image, output_image_path, final_prompt)
        reflection_result = self.registry.call("reflection", caption, final_prompt, score)
        retry_needed = self.registry.call("retry", score)

        retry_output_image_path = None
        retry_score = None

        if retry_needed:
            print("[OrchestratorAgent] Retry needed. Starting second attempt.")
            retry_output_image_path = self.registry.call(
                "generation",
                reflection_result["suggested_prompt"]
            )
            retry_score = self.registry.call(
                "evaluation",
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
            history_path = self.registry.call(
                "memory_save",
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
            "planner_result": planner_result,
            "agent_trace": [
                "PlannerAgent generated execution plan",
                "ToolRegistry called memory_load",
                "ToolRegistry called vision",
                "OrchestratorAgent built prompt context",
                "ToolRegistry called prompt",
                "PromptAgent generated context-aware prompt",
                "ToolRegistry called generation",
                "ToolRegistry called evaluation",
                "ToolRegistry called reflection",
                "ToolRegistry called retry",
                "OrchestratorAgent selected best result",
                (
                    "ToolRegistry called memory_save"
                    if memory_saved
                    else "ToolRegistry memory_save skipped after error"
                ),
            ],
        }
