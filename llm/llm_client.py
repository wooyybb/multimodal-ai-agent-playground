import os

from llm.model_service import AIModelService


class LLMClient:
    def __init__(self, provider: str | None = None):
        self.provider_name = provider or os.getenv("LLM_PROVIDER", "mock")
        self.model_service = AIModelService(self.provider_name)
        print(f"[LLM Layer] Provider: {self.provider_name}")

    def reason(self, state: dict) -> dict:
        return self.model_service.reason(state or {})

    def critic(self, state: dict, mode: str = "mock") -> dict:
        return self.model_service.critic(state or {}, mode=mode)

    def optimize(self, state: dict, mode: str = "mock") -> dict:
        return self.model_service.optimize(state or {}, mode=mode)
