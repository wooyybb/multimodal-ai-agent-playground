from llm.llm_client import LLMClient


class LLMContextReasoner:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or LLMClient()

    def run(self, state: dict) -> dict:
        print("[LLMContextReasoner] Running...")
        reasoning = self.llm_client.reason(state or {})
        print(f"[LLMContextReasoner] User Goal: {reasoning['user_goal']}")
        print(f"[LLMContextReasoner] Scene Goal: {reasoning['scene_goal']}")
        return {"context_reasoning": reasoning}
