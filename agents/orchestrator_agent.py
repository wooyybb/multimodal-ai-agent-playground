from agents.planning_agent import PlannerAgent
from core import state_keys as keys
from core.result_builder import build_pipeline_result
from registry import build_tool_registry
from workflow.execution_engine import DynamicExecutionEngine


class OrchestratorAgent:
    def __init__(self):
        self.planner_agent = PlannerAgent()
        self.registry = build_tool_registry()
        self.execution_engine = DynamicExecutionEngine()

    def run(self, image, user_prompt, provider=None):
        print("[OrchestratorAgent] Starting workflow coordination...")
        planner_result = self.planner_agent.run(
            user_prompt=user_prompt,
            image_provided=image is not None,
        )
        state = self._build_initial_state(image, user_prompt, provider, planner_result)
        final_state = self.execution_engine.run(
            planner_result.get("execution_plan", []),
            self.registry,
            state,
        )
        print("[OrchestratorAgent] Workflow coordination finished.")
        return build_pipeline_result(final_state, planner_result)

    def _build_initial_state(self, image, user_prompt, provider, planner_result):
        return {
            keys.IMAGE: image,
            keys.USER_PROMPT: user_prompt,
            keys.REQUESTED_PROVIDER: provider,
            keys.PROVIDER: provider,
            keys.PLANNER_RESULT: planner_result,
            keys.AGENT_TRACE: ["PlanningAgent generated execution plan"],
        }
