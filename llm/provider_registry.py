from llm.mock_llm import MockLLM


class LLMProviderRegistry:
    SUPPORTED_PROVIDERS = ("mock", "future", "openai", "gemini", "claude", "ollama")

    def get_provider(self, provider_name: str):
        provider = str(provider_name or "mock").lower()
        if provider != "mock":
            print(
                f"[LLMClient] Provider '{provider}' is registered as future; "
                "using Mock provider fallback."
            )
        return MockLLM()
