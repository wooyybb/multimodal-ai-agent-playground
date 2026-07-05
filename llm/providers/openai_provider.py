import os
import time

from llm.providers.base_provider import BaseProvider
from llm.providers.mock_provider import MockProvider
from llm.json_parser import JSONParser


class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.fallback = MockProvider()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL") or "gpt-4.1-mini"
        self.parser = JSONParser()
        self.client = self._build_client()

    def reason(self, state: dict) -> dict:
        fallback = self.fallback.reason(state or {})
        if not self.client:
            self._log_result(False, True, 0.0)
            return self._with_fallback_reason(fallback, "OpenAI API key or client unavailable.")

        system_prompt = (
            "You are a semantic planning model. Return only JSON with keys: "
            "user_goal, scene_goal, composition_goal, interaction_goal, style_goal, priority."
        )
        user_payload = {
            "task": "reason",
            "input": state or {},
        }
        parsed, raw_text, used_fallback, latency = self._request_json(
            system_prompt,
            user_payload,
        )
        if used_fallback:
            return self._with_fallback_reason(
                fallback,
                "OpenAI response was not valid JSON.",
                raw_text,
                latency,
            )

        return {
            "user_goal": parsed.get("user_goal", fallback["user_goal"]),
            "scene_goal": parsed.get("scene_goal", fallback["scene_goal"]),
            "composition_goal": parsed.get("composition_goal", fallback["composition_goal"]),
            "interaction_goal": parsed.get("interaction_goal", fallback["interaction_goal"]),
            "style_goal": parsed.get("style_goal", fallback["style_goal"]),
            "priority": parsed.get("priority", fallback["priority"]),
            "mode": "openai",
            "used_fallback": False,
            "llm_provider": "openai",
            "llm_used_fallback": False,
            "llm_json_parse_success": True,
            "llm_reasoning_latency": latency,
        }

    def critic(self, state: dict, mode: str = "mock") -> dict:
        if mode in {"disabled", "mock"}:
            return self.fallback.critic(state or {}, mode=mode)

        fallback = self.fallback.critic(state or {}, mode="llm")
        if not self.client:
            self._log_result(False, True, 0.0)
            return self._with_fallback_report(fallback, "OpenAI API key or client unavailable.")

        system_prompt = (
            "You are a prompt critic. Return only JSON with keys: "
            "critic_score, semantic_issues, conflicts, priority_issues, "
            "provider_suitability_issues, suggestions, priority_fix, reasoning_summary."
        )
        user_payload = {
            "task": "critic",
            "input": state or {},
        }
        parsed, raw_text, used_fallback, latency = self._request_json(
            system_prompt,
            user_payload,
        )
        if used_fallback:
            return self._with_fallback_report(
                fallback,
                "OpenAI response was not valid JSON.",
                raw_text,
                latency,
            )

        return {
            "mode": "openai",
            "critic_score": int(parsed.get("critic_score", fallback["critic_score"])),
            "semantic_issues": self._list(parsed.get("semantic_issues")),
            "conflicts": self._list(parsed.get("conflicts")),
            "priority_issues": self._list(parsed.get("priority_issues")),
            "provider_suitability_issues": self._list(
                parsed.get("provider_suitability_issues")
            ),
            "suggestions": self._list(parsed.get("suggestions")),
            "priority_fix": self._list(parsed.get("priority_fix")),
            "reasoning_summary": parsed.get("reasoning_summary", ""),
            "used_fallback": False,
            "llm_provider": "openai",
            "llm_used_fallback": False,
            "llm_json_parse_success": True,
            "llm_reasoning_latency": latency,
        }

    def optimize(self, state: dict, mode: str = "mock") -> dict:
        if mode in {"disabled", "mock"}:
            return self.fallback.optimize(state or {}, mode=mode)

        fallback = self.fallback.optimize(state or {}, mode="llm")
        if not self.client:
            self._log_result(False, True, 0.0)
            return self._with_fallback_optimizer(
                fallback,
                "OpenAI API key or client unavailable.",
            )

        system_prompt = (
            "You are a prompt optimizer. Return only JSON with keys: "
            "optimized_prompt, changes, reason."
        )
        user_payload = {
            "task": "optimize",
            "input": state or {},
        }
        parsed, raw_text, used_fallback, latency = self._request_json(
            system_prompt,
            user_payload,
        )
        if used_fallback:
            return self._with_fallback_optimizer(
                fallback,
                "OpenAI response was not valid JSON.",
                raw_text,
                latency,
            )

        optimized_prompt = parsed.get("optimized_prompt") or (
            state.get("canonical_prompt") or state.get("final_prompt") or ""
        )
        return {
            "llm_optimized_prompt": optimized_prompt,
            "canonical_prompt": optimized_prompt,
            "final_prompt": optimized_prompt,
            "llm_optimizer_report": {
                "mode": "openai",
                "reason": parsed.get("reason", "OpenAI optimizer returned structured output."),
                "changes": self._list(parsed.get("changes")),
                "used_fallback": False,
                "llm_provider": "openai",
                "llm_used_fallback": False,
                "llm_json_parse_success": True,
                "llm_reasoning_latency": latency,
            },
        }

    def _build_client(self):
        if not self.api_key:
            print("[OpenAIProvider] Warning: OPENAI_API_KEY missing. Using Mock fallback.")
            return None
        try:
            from openai import OpenAI

            return OpenAI(api_key=self.api_key)
        except Exception as error:
            print(f"[OpenAIProvider] Warning: OpenAI client unavailable: {error}")
            return None

    def _request_json(self, system_prompt, user_payload):
        started = time.perf_counter()
        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": json.dumps(user_payload, ensure_ascii=False),
                    },
                ],
            )
            raw_text = getattr(response, "output_text", "") or str(response)
            parsed, failed = self.parser.parse(raw_text)
            latency = round(time.perf_counter() - started, 4)
            self._log_result(not failed, failed, latency)
            return parsed, raw_text if failed else "", bool(failed), latency
        except Exception as error:
            print(f"[OpenAIProvider] Warning: OpenAI request failed: {error}")
            latency = round(time.perf_counter() - started, 4)
            self._log_result(False, True, latency)
            return {}, str(error), True, latency

    def _with_fallback_reason(self, fallback, reason, raw_text=None, latency=0.0):
        result = dict(fallback)
        result["mode"] = "openai_fallback"
        result["used_fallback"] = True
        result["fallback_reason"] = reason
        result["llm_provider"] = "openai"
        result["llm_used_fallback"] = True
        result["llm_json_parse_success"] = False
        result["llm_reasoning_latency"] = latency
        if raw_text is not None:
            result["raw_text"] = raw_text
            result["llm_reasoning_raw_text"] = raw_text
        return result

    def _with_fallback_report(self, fallback, reason, raw_text=None, latency=0.0):
        result = dict(fallback)
        result["mode"] = "openai_fallback"
        result["used_fallback"] = True
        result["reasoning_summary"] = reason
        result["llm_provider"] = "openai"
        result["llm_used_fallback"] = True
        result["llm_json_parse_success"] = False
        result["llm_reasoning_latency"] = latency
        if raw_text is not None:
            result["raw_text"] = raw_text
            result["llm_reasoning_raw_text"] = raw_text
        return result

    def _with_fallback_optimizer(self, fallback, reason, raw_text=None, latency=0.0):
        result = dict(fallback)
        report = dict(result.get("llm_optimizer_report") or {})
        report["mode"] = "openai_fallback"
        report["reason"] = reason
        report["used_fallback"] = True
        report["llm_provider"] = "openai"
        report["llm_used_fallback"] = True
        report["llm_json_parse_success"] = False
        report["llm_reasoning_latency"] = latency
        if raw_text is not None:
            report["raw_text"] = raw_text
            report["llm_reasoning_raw_text"] = raw_text
        result["llm_optimizer_report"] = report
        return result

    def _log_result(self, parse_success, used_fallback, latency):
        print("[LLM Layer] Provider: openai")
        print(f"[LLM Layer] Used fallback: {bool(used_fallback)}")
        print(f"[LLM Layer] JSON parse success: {bool(parse_success)}")
        print(f"[LLM Layer] Reasoning latency: {latency}s")

    def _list(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]
