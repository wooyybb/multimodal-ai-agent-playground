from memory.history import MemoryManager
from modules.evaluation.evaluation_agent import EvaluationAgent
from modules.generation.generation_agent import GenerationAgent
from modules.generation.prompt_compiler import PromptCompiler
from modules.generation.provider_prompt_adapter import ProviderPromptAdapter
from modules.generation.provider_router import ProviderRouter
from modules.planning.character_agent import CharacterAgent
from modules.planning.context_program_builder import ContextProgramBuilder
from modules.planning.context_program_validator import ContextProgramValidator
from modules.planning.expression_agent import ExpressionAgent
from modules.planning.layout_agent import LayoutAgent
from modules.planning.lighting_agent import LightingAgent
from modules.planning.negative_prompt_agent import NegativePromptAgent
from modules.planning.pose_agent import PoseAgent
from modules.planning.retrieval_agent import RetrievalAgent
from modules.planning.scene_planning_agent import ScenePlanningAgent
from modules.planning.style_agent import StyleAgent
from modules.prompt.llm_prompt_critic_agent import LLMPromptCriticAgent
from modules.prompt.llm_prompt_optimizer_agent import LLMPromptOptimizerAgent
from modules.prompt.prompt_agent import PromptAgent
from modules.prompt.prompt_assembler import PromptAssembler
from modules.prompt.prompt_compressor import PromptCompressor
from modules.prompt.prompt_critic_agent import PromptCriticAgent
from modules.prompt.prompt_optimizer_agent import PromptOptimizerAgent
from modules.reflection.reflection_agent import ReflectionAgent
from modules.reflection.retry_agent import RetryAgent
from modules.understanding.vision_agent import VisionAgent
from registry.tool_registry import ToolRegistry


def build_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    memory_manager = MemoryManager()
    register_infrastructure_tools(registry, memory_manager)
    register_understanding_tools(registry)
    register_planning_tools(registry)
    register_generation_tools(registry)
    register_evaluation_tools(registry)
    register_reflection_tools(registry)
    return registry


def register_understanding_tools(registry):
    registry.register("vision", VisionAgent(), agent_group="understanding")


def register_planning_tools(registry):
    registry.register("retrieval", RetrievalAgent(), agent_group="planning")
    registry.register("prompt_compressor", PromptCompressor(), agent_group="planning")
    registry.register("scene_planning", ScenePlanningAgent(), agent_group="planning")
    registry.register("character", CharacterAgent(), agent_group="planning")
    registry.register("style", StyleAgent(), agent_group="planning")
    registry.register("layout", LayoutAgent(), agent_group="planning")
    registry.register("pose", PoseAgent(), agent_group="planning")
    registry.register("expression", ExpressionAgent(), agent_group="planning")
    registry.register("lighting", LightingAgent(), agent_group="planning")
    registry.register("negative_prompt", NegativePromptAgent(), agent_group="planning")
    registry.register(
        "context_program_builder",
        ContextProgramBuilder(),
        agent_group="planning",
    )
    registry.register(
        "context_program_validator",
        ContextProgramValidator(),
        agent_group="planning",
    )
    registry.register("prompt_assembler", PromptAssembler(), agent_group="planning")
    registry.register("prompt_critic", PromptCriticAgent(), agent_group="planning")
    registry.register(
        "llm_prompt_critic",
        LLMPromptCriticAgent(),
        agent_group="planning",
    )
    registry.register(
        "prompt_optimizer",
        PromptOptimizerAgent(),
        agent_group="planning",
    )
    registry.register(
        "llm_prompt_optimizer",
        LLMPromptOptimizerAgent(),
        agent_group="planning",
    )
    registry.register("prompt", PromptAgent(), agent_group="planning")


def register_generation_tools(registry):
    registry.register("provider_router", ProviderRouter(), agent_group="generation")
    registry.register("prompt_compiler", PromptCompiler(), agent_group="generation")
    registry.register(
        "provider_prompt_adapter",
        ProviderPromptAdapter(),
        agent_group="generation",
    )
    registry.register("generation", GenerationAgent(), agent_group="generation")


def register_evaluation_tools(registry):
    registry.register("evaluation", EvaluationAgent(), agent_group="evaluation")


def register_reflection_tools(registry):
    retry_agent = RetryAgent()
    registry.register("reflection", ReflectionAgent(), agent_group="reflection")
    registry.register("retry", retry_agent.should_retry, agent_group="reflection")


def register_infrastructure_tools(registry, memory_manager):
    registry.register(
        "memory_load",
        memory_manager.load_last_run,
        agent_group="infrastructure",
    )
    registry.register(
        "memory_retrieval",
        memory_manager.get_memory_context,
        agent_group="planning",
    )
    registry.register(
        "memory_save",
        memory_manager.save_run,
        agent_group="infrastructure",
    )
