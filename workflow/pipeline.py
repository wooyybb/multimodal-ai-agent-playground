from agents.orchestrator_agent import OrchestratorAgent


class MultimodalPipeline:
    def __init__(self):
        self.orchestrator_agent = OrchestratorAgent()

    def run(self, image, user_prompt):
        print("[Pipeline] Starting multi-agent pipeline...")
        result = self.orchestrator_agent.run(image, user_prompt)
        print("[Pipeline] Finished pipeline.")
        return result
