from llm.providers.claude_provider import ClaudeProvider
from llm.providers.gemini_provider import GeminiProvider
from llm.providers.mock_provider import MockProvider
from llm.providers.ollama_provider import OllamaProvider
from llm.providers.openai_provider import OpenAIProvider


class LLMProviderRegistry:
    SUPPORTED_PROVIDERS = ("mock", "openai", "gemini", "claude", "ollama")

    def get_provider(self, provider_name: str):
        provider = str(provider_name or "mock").lower()
        providers = {
            "mock": MockProvider,
            "openai": OpenAIProvider,
            "gemini": GeminiProvider,
            "claude": ClaudeProvider,
            "ollama": OllamaProvider,
        }
        provider_class = providers.get(provider)
        if provider_class is None:
            print(f"[AIModelService] Unknown provider '{provider}', using Mock.")
            provider_class = MockProvider
        return provider_class()
