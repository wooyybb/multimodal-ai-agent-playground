from workflow.agent_state import AgentState


class ToolRegistry:
    AGENT_GROUP_METADATA = {
        "understanding": [
            "vision",
            "reference_image_parser",
            "character_program_builder",
        ],
        "planning": [
            "llm_context_reasoner",
            "goal_planner",
            "scene_planning",
            "character",
            "style",
            "layout",
            "pose",
            "expression",
            "lighting",
            "negative_prompt",
            "context_program_builder",
            "context_program_validator",
            "prompt_assembler",
            "prompt_critic",
            "llm_prompt_critic",
            "prompt_optimizer",
            "llm_prompt_optimizer",
            "retrieval",
            "memory_retrieval",
            "prompt_compressor",
        ],
        "generation": [
            "prompt_compiler",
            "provider_router",
            "provider_prompt_adapter",
            "generation",
        ],
        "evaluation": [
            "evaluation",
        ],
        "reflection": [
            "reflection",
            "self_verification",
            "strategy_selector",
            "adaptive_planner",
            "retry",
        ],
        "infrastructure": [
            "memory_load",
            "memory_save",
        ],
    }
    AGENT_GROUP_LABELS = {
        "understanding": "Understanding Agent",
        "planning": "Planning Agent",
        "generation": "Generation Agent",
        "evaluation": "Evaluation Agent",
        "reflection": "Reflection Agent",
        "infrastructure": "Infrastructure",
        "unmapped": "Unmapped Agent",
    }
    LAYER_METADATA = {
        "planning": [
            "goal_planner",
            "vision",
            "reference_image_parser",
            "character_program_builder",
            "scene_planning",
            "llm_context_reasoner",
        ],
        "context": [
            "retrieval",
            "memory_retrieval",
            "prompt_compressor",
            "character",
            "style",
            "layout",
            "pose",
            "expression",
            "lighting",
            "context_program_builder",
            "context_program_validator",
            "prompt_assembler",
            "negative_prompt",
            "prompt_critic",
            "llm_prompt_critic",
            "prompt_optimizer",
            "llm_prompt_optimizer",
            "prompt_compiler",
        ],
        "generation": [
            "provider_router",
            "provider_prompt_adapter",
            "generation",
        ],
        "evaluation": [
            "evaluation",
            "reflection",
            "self_verification",
            "strategy_selector",
            "adaptive_planner",
            "retry",
        ],
        "infrastructure": [
            "memory_load",
            "memory_save",
        ],
    }
    LAYER_LABELS = {
        "planning": "Planning Layer",
        "context": "Context Layer",
        "generation": "Generation Layer",
        "evaluation": "Evaluation Layer",
        "infrastructure": "Infrastructure Layer",
        "unmapped": "Unmapped Layer",
    }

    def __init__(self):
        self._tools = {}
        self._register_default_tools()

    def _register_default_tools(self):
        try:
            from modules.planning.llm_context_reasoner import LLMContextReasoner

            self.register("llm_context_reasoner", LLMContextReasoner())
            from modules.reflection.adaptive_planner import AdaptivePlanner

            self.register("adaptive_planner", AdaptivePlanner())
            from modules.understanding.character_program_builder import CharacterProgramBuilder

            self.register("character_program_builder", CharacterProgramBuilder())
            from modules.understanding.reference_image_parser import ReferenceImageParser

            self.register("reference_image_parser", ReferenceImageParser())
            from modules.planning.goal_planner import GoalPlanner

            self.register("goal_planner", GoalPlanner())
            from modules.reflection.strategy_selector import StrategySelector

            self.register("strategy_selector", StrategySelector())
            from modules.reflection.self_verification_agent import SelfVerificationAgent

            self.register("self_verification", SelfVerificationAgent())
        except Exception as error:
            print(f"[ToolRegistry] Default tool registration skipped: {error}")

    def register(self, name: str, callable_obj):
        print(f"[ToolRegistry] Registering tool: {name}")
        self._tools[name] = callable_obj

    def call(self, name: str, *args, **kwargs):
        print(f"[ToolRegistry] Calling tool: {name}")

        if name not in self._tools:
            raise ValueError(f"Tool is not registered: {name}")

        tool = self._tools[name]
        if hasattr(tool, "run"):
            return tool.run(*args, **kwargs)
        if callable(tool):
            return tool(*args, **kwargs)

        raise ValueError(f"Registered tool is not callable: {name}")

    def run_with_state(self, name: str, state: dict) -> dict:
        print(f"[ToolRegistry] Running state-based tool: {name}")

        if name not in self._tools:
            raise ValueError(f"Tool is not registered: {name}")

        tool = self._tools[name]
        state_payload = state.to_dict() if isinstance(state, AgentState) else state
        if hasattr(tool, "run"):
            result = tool.run(state_payload)
        elif callable(tool):
            result = tool(state_payload)
        else:
            raise ValueError(f"Registered tool is not callable: {name}")

        if result is None:
            result = {}
        if not isinstance(result, dict):
            print(
                f"[ToolRegistry] Warning: {name} returned "
                f"{type(result).__name__}; wrapping result."
            )
            result = {name: result}

        print(f"[ToolRegistry] State update keys: {list(result.keys())}")
        if isinstance(state, AgentState):
            state.update_from_dict(result)
        return result

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    def layer_for(self, tool_name: str) -> str:
        for layer, tools in self.LAYER_METADATA.items():
            if tool_name in tools:
                return layer
        return "unmapped"

    def layer_label_for(self, tool_name: str) -> str:
        return self.LAYER_LABELS.get(self.layer_for(tool_name), "Unmapped Layer")

    def agent_group_for(self, tool_name: str) -> str:
        for group, tools in self.AGENT_GROUP_METADATA.items():
            if tool_name in tools:
                return group
        return "unmapped"

    def agent_group_label_for(self, tool_name: str) -> str:
        return self.AGENT_GROUP_LABELS.get(
            self.agent_group_for(tool_name), "Unmapped Agent"
        )

    def metadata_for(self, tool_name: str) -> dict:
        return {
            "name": tool_name,
            "layer": self.layer_for(tool_name),
            "layer_label": self.layer_label_for(tool_name),
            "agent_group": self.agent_group_for(tool_name),
            "agent_group_label": self.agent_group_label_for(tool_name),
        }
