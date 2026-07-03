from llm.providers.base_provider import BaseProvider
from llm.providers.mock_provider import MockProvider


class OllamaProvider(BaseProvider):
    def __init__(self):
        self.fallback = MockProvider()

    def reason(self, state: dict) -> dict:
        # TODO: Connect Ollama local API in a future sprint.
        return self.fallback.reason(state)

    def critic(self, state: dict, mode: str = "mock") -> dict:
        # TODO: Connect Ollama local API in a future sprint.
        return self.fallback.critic(state, mode="llm")

    def optimize(self, state: dict, mode: str = "mock") -> dict:
        # TODO: Connect Ollama local API in a future sprint.
        return self.fallback.optimize(state, mode="llm")
