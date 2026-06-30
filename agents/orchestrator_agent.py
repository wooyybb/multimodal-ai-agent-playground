from agents.evaluation_agent import EvaluationAgent
from agents.generation_agent import GenerationAgent
from agents.planner_agent import PlannerAgent
from agents.prompt_compressor import PromptCompressor
from agents.prompt_agent import PromptAgent
from agents.reflection_agent import ReflectionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.retry_agent import RetryAgent
from agents.vision_agent import VisionAgent
from memory.history import MemoryManager
from registry import ToolRegistry
from workflow.execution_engine import DynamicExecutionEngine


class OrchestratorAgent:
    def __init__(self):
        self.planner_agent = PlannerAgent()
        self.prompt_compressor = PromptCompressor()
        self.retrieval_agent = RetrievalAgent()
        self.vision_agent = VisionAgent()
        self.prompt_agent = PromptAgent()
        self.generation_agent = GenerationAgent()
        self.evaluation_agent = EvaluationAgent()
        self.reflection_agent = ReflectionAgent()
        self.retry_agent = RetryAgent()
        self.memory_manager = MemoryManager()
        self.registry = ToolRegistry()
        self.execution_engine = DynamicExecutionEngine()
        self._register_tools()

    def _register_tools(self):
        self.registry.register("memory_load", self.memory_manager.load_last_run)
        self.registry.register(
            "memory_retrieval",
            self.memory_manager.get_memory_context,
        )
        self.registry.register("vision", self.vision_agent)
        self.registry.register("retrieval", self.retrieval_agent)
        self.registry.register("prompt_compressor", self.prompt_compressor)
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

        state = {
            "image": image,
            "user_prompt": user_prompt,
            "planner_result": planner_result,
            "agent_trace": ["PlannerAgent generated execution plan"],
        }
        final_state = self.execution_engine.run(
            planner_result.get("execution_plan", []),
            self.registry,
            state,
        )
        print("[OrchestratorAgent] Multi-agent workflow finished.")

        return {
            "caption": final_state.get("caption"),
            "final_prompt": final_state.get("final_prompt"),
            "output_image_path": final_state.get("output_image_path"),
            "score": final_state.get("score"),
            "retry_needed": final_state.get("retry_needed"),
            "retry_output_image_path": final_state.get("retry_output_image_path"),
            "retry_score": final_state.get("retry_score"),
            "reflection": final_state.get("reflection"),
            "suggested_prompt": final_state.get("suggested_prompt"),
            "best_prompt": final_state.get("best_prompt"),
            "best_output_image_path": final_state.get("best_output_image_path"),
            "best_score": final_state.get("best_score"),
            "history_path": final_state.get("history_path"),
            "last_run": final_state.get("last_run"),
            "memory_context": final_state.get("memory_context"),
            "memory_saved": final_state.get("memory_saved", False),
            "planner_result": planner_result,
            "prompt_context": final_state.get("prompt_context"),
            "retrieved_context": final_state.get("retrieved_context"),
            "compressed_context": final_state.get("compressed_context"),
            "agent_trace": final_state.get("agent_trace", []),
        }
