import os
import time

from llm.openai_reasoner import OpenAIReasoner


class ReasonerRouter:
    def __init__(self, provider: str | None = None):
        self.provider = str(provider or os.getenv("LLM_PROVIDER", "rule")).lower()

    def reason(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        fallback: dict | None = None,
        schema_name: str = "generic",
    ) -> dict:
        fallback = fallback or {}
        started = time.perf_counter()
        print(f"[ReasonerRouter] Provider: {self.provider}")

        if self.provider in ("rule", "mock", "none", ""):
            return self._finish(fallback, started, True, "rule fallback", schema_name)

        if self.provider == "openai":
            result = OpenAIReasoner().reason(system_prompt, user_prompt)
            if result.get("used_fallback"):
                merged = dict(fallback)
                merged["reasoning_fallback_reason"] = result.get("fallback_reason")
                return self._finish(merged, started, True, "openai fallback", schema_name)
            result["reasoning_provider"] = "openai"
            return self._finish(result, started, False, "", schema_name)

        if self.provider in ("gemini", "claude"):
            merged = dict(fallback)
            merged["reasoning_fallback_reason"] = f"{self.provider} reasoner skeleton is not implemented."
            return self._finish(merged, started, True, f"{self.provider} fallback", schema_name)

        merged = dict(fallback)
        merged["reasoning_fallback_reason"] = f"Unknown reasoner provider: {self.provider}"
        return self._finish(merged, started, True, "unknown provider fallback", schema_name)

    def _finish(self, result, started, used_fallback, reason, schema_name):
        latency = round(time.perf_counter() - started, 4)
        print(f"[ReasonerRouter] Fallback: {used_fallback}")
        print(f"[ReasonerRouter] Latency: {latency}s")
        output = dict(result or {})
        output.setdefault("reasoning_provider", self.provider)
        output["reasoning_schema"] = schema_name
        output["reasoning_used_fallback"] = bool(used_fallback)
        output["reasoning_latency"] = latency
        if reason:
            output.setdefault("reasoning_fallback_reason", reason)
        return output
