import os

from llm.provider_registry import LLMProviderRegistry


class LLMClient:
    def __init__(self, provider: str | None = None):
        self.provider_name = provider or os.getenv("LLM_PROVIDER", "mock")
        self.registry = LLMProviderRegistry()
        self.provider = self.registry.get_provider(self.provider_name)
        print(f"[LLMClient] Provider: {self.provider_name}")

    def reason(self, state: dict) -> dict:
        return self.provider.reason(state or {})

    def critic(self, state: dict, mode: str = "mock") -> dict:
        return self.provider.critic(state or {}, mode=mode)

    def optimize(self, state: dict, mode: str = "mock") -> dict:
        return self.provider.optimize(state or {}, mode=mode)
