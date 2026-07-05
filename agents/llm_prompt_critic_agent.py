import os

from llm.llm_client import LLMClient


class LLMPromptCriticAgent:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or LLMClient()

    def run(self, state: dict) -> dict:
        print("[LLMPromptCritic] Running...")
        state = state or {}
        mode = self._mode()

        try:
            report = self.llm_client.critic(state, mode=mode)
        except Exception as error:
            print(f"[LLMPromptCritic] Error: {error}")
            report = self.llm_client.critic(
                {
                    **state,
                    "prompt_report": {
                        "suggestions": [
                            "LLM prompt critic failed; keep rule-based critic result"
                        ]
                    },
                },
                mode="disabled",
            )
            report["reasoning_summary"] = str(error)
            report["used_fallback"] = True

        print(f"[LLMPromptCritic] Mode: {report['mode']}")
        print(f"[LLMPromptCritic] Critic score: {report['critic_score']}")
        print(f"[LLMPromptCritic] Conflicts: {report['conflicts']}")
        print(f"[LLMPromptCritic] Suggestions: {report['suggestions']}")
        return {
            "llm_prompt_critic_report": report,
            "llm_prompt_critic_score": report["critic_score"],
        }

    def _mode(self):
        if os.getenv("LLM_PROVIDER", "").lower() == "openai":
            return "llm"
        enabled = os.getenv("LLM_PROMPT_CRITIC_ENABLED", "").lower() == "true"
        mock = os.getenv("LLM_PROMPT_CRITIC_MOCK", "").lower() == "true"
        if not enabled:
            return "disabled"
        if mock:
            return "mock"
        return "llm"
