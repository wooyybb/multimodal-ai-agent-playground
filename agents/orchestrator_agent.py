from agents.character_agent import CharacterAgent
from agents.evaluation_agent import EvaluationAgent
from agents.generation_agent import GenerationAgent
from agents.layout_agent import LayoutAgent
from agents.lighting_agent import LightingAgent
from agents.negative_prompt_agent import NegativePromptAgent
from agents.planner_agent import PlannerAgent
from agents.pose_agent import PoseAgent
from agents.expression_agent import ExpressionAgent
from agents.prompt_assembler import PromptAssembler
from agents.prompt_critic_agent import PromptCriticAgent
from agents.provider_prompt_adapter import ProviderPromptAdapter
from agents.provider_router import ProviderRouter
from agents.prompt_compressor import PromptCompressor
from agents.prompt_agent import PromptAgent
from agents.reflection_agent import ReflectionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.retry_agent import RetryAgent
from agents.scene_planning_agent import ScenePlanningAgent
from agents.vision_agent import VisionAgent
from agents.style_agent import StyleAgent
from memory.history import MemoryManager
from registry import ToolRegistry
from workflow.execution_engine import DynamicExecutionEngine


class OrchestratorAgent:
    def __init__(self):
        self.planner_agent = PlannerAgent()
        self.character_agent = CharacterAgent()
        self.style_agent = StyleAgent()
        self.layout_agent = LayoutAgent()
        self.pose_agent = PoseAgent()
        self.expression_agent = ExpressionAgent()
        self.lighting_agent = LightingAgent()
        self.negative_prompt_agent = NegativePromptAgent()
        self.prompt_assembler = PromptAssembler()
        self.prompt_critic_agent = PromptCriticAgent()
        self.provider_router = ProviderRouter()
        self.provider_prompt_adapter = ProviderPromptAdapter()
        self.scene_planning_agent = ScenePlanningAgent()
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
        self.registry.register("scene_planning", self.scene_planning_agent)
        self.registry.register("character", self.character_agent)
        self.registry.register("style", self.style_agent)
        self.registry.register("layout", self.layout_agent)
        self.registry.register("pose", self.pose_agent)
        self.registry.register("expression", self.expression_agent)
        self.registry.register("lighting", self.lighting_agent)
        self.registry.register("negative_prompt", self.negative_prompt_agent)
        self.registry.register("prompt_assembler", self.prompt_assembler)
        self.registry.register("prompt_critic", self.prompt_critic_agent)
        self.registry.register("provider_router", self.provider_router)
        self.registry.register("provider_prompt_adapter", self.provider_prompt_adapter)
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
            "scene_plan": final_state.get("scene_plan"),
            "character_section": final_state.get("character_section"),
            "style_section": final_state.get("style_section"),
            "layout_section": final_state.get("layout_section"),
            "pose_section": final_state.get("pose_section"),
            "expression_section": final_state.get("expression_section"),
            "lighting_section": final_state.get("lighting_section"),
            "negative_prompt": final_state.get("negative_prompt"),
            "canonical_prompt": final_state.get("canonical_prompt"),
            "prompt_report": final_state.get("prompt_report"),
            "prompt_quality_score": final_state.get("prompt_quality_score"),
            "provider_routing": final_state.get("provider_routing"),
            "provider": final_state.get("provider"),
            "provider_prompt": final_state.get("provider_prompt"),
            "provider_negative_prompt": final_state.get("provider_negative_prompt"),
            "adapter_notes": final_state.get("adapter_notes"),
            "prompt_sections": final_state.get("prompt_sections"),
            "agent_trace": final_state.get("agent_trace", []),
        }
