from agents.orchestrator_agent import OrchestratorAgent


class MultimodalPipeline:
    def __init__(self):
        self.orchestrator_agent = OrchestratorAgent()

    def run(self, image, user_prompt):
        print("[Pipeline] Running from UI...")
        print("[Pipeline] Starting multi-agent pipeline...")
        result = self.orchestrator_agent.run(image, user_prompt)
        if not isinstance(result, dict):
            result = {}
        result.setdefault("agent_trace", [])
        if not isinstance(result["agent_trace"], list):
            result["agent_trace"] = []
        print("[Pipeline] Finished pipeline.")
        return result
