from workflow.agent_state import AgentState


class ToolRegistry:
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
            from agents.llm_context_reasoner import LLMContextReasoner

            self.register("llm_context_reasoner", LLMContextReasoner())
            from agents.adaptive_planner import AdaptivePlanner

            self.register("adaptive_planner", AdaptivePlanner())
            from agents.character_program_builder import CharacterProgramBuilder

            self.register("character_program_builder", CharacterProgramBuilder())
            from agents.reference_image_parser import ReferenceImageParser

            self.register("reference_image_parser", ReferenceImageParser())
            from agents.goal_planner import GoalPlanner

            self.register("goal_planner", GoalPlanner())
            from agents.strategy_selector import StrategySelector

            self.register("strategy_selector", StrategySelector())
            from agents.self_verification_agent import SelfVerificationAgent

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
