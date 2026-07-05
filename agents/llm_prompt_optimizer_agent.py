import os

from llm.llm_client import LLMClient


class LLMPromptOptimizerAgent:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or LLMClient()

    def run(self, state: dict) -> dict:
        print("[LLMPromptOptimizer] Running...")
        state = state or {}
        mode = self._mode()
        print(f"[LLMPromptOptimizer] Mode: {mode}")
        result = self.llm_client.optimize(state, mode=mode)
        print(
            "[LLMPromptOptimizer] Used fallback: "
            f"{result['llm_optimizer_report']['used_fallback']}"
        )
        return result

    def _mode(self):
        if os.getenv("LLM_PROVIDER", "").lower() == "openai":
            return "llm"
        if os.getenv("LLM_OPTIMIZER_MOCK", "").lower() == "true":
            return "mock"
        if os.getenv("LLM_OPTIMIZER_ENABLED", "").lower() == "true":
            return "llm"
        return "disabled"
