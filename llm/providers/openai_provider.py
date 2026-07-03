import json
import os

from llm.providers.base_provider import BaseProvider
from llm.providers.mock_provider import MockProvider


class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.fallback = MockProvider()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.5")
        self.client = self._build_client()

    def reason(self, state: dict) -> dict:
        fallback = self.fallback.reason(state or {})
        if not self.client:
            return self._with_fallback_reason(fallback, "OpenAI API key or client unavailable.")

        system_prompt = (
            "You are a semantic planning model. Return only JSON with keys: "
            "user_goal, scene_goal, composition_goal, interaction_goal, style_goal, priority."
        )
        user_payload = {
            "task": "reason",
            "input": state or {},
        }
        parsed, raw_text, used_fallback = self._request_json(system_prompt, user_payload)
        if used_fallback:
            return self._with_fallback_reason(fallback, "OpenAI response was not valid JSON.", raw_text)

        return {
            "user_goal": parsed.get("user_goal", fallback["user_goal"]),
            "scene_goal": parsed.get("scene_goal", fallback["scene_goal"]),
            "composition_goal": parsed.get("composition_goal", fallback["composition_goal"]),
            "interaction_goal": parsed.get("interaction_goal", fallback["interaction_goal"]),
            "style_goal": parsed.get("style_goal", fallback["style_goal"]),
            "priority": parsed.get("priority", fallback["priority"]),
            "mode": "openai",
            "used_fallback": False,
        }

    def critic(self, state: dict, mode: str = "mock") -> dict:
        if mode in {"disabled", "mock"}:
            return self.fallback.critic(state or {}, mode=mode)

        fallback = self.fallback.critic(state or {}, mode="llm")
        if not self.client:
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
        parsed, raw_text, used_fallback = self._request_json(system_prompt, user_payload)
        if used_fallback:
            return self._with_fallback_report(
                fallback,
                "OpenAI response was not valid JSON.",
                raw_text,
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
        }

    def optimize(self, state: dict, mode: str = "mock") -> dict:
        if mode in {"disabled", "mock"}:
            return self.fallback.optimize(state or {}, mode=mode)

        fallback = self.fallback.optimize(state or {}, mode="llm")
        if not self.client:
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
        parsed, raw_text, used_fallback = self._request_json(system_prompt, user_payload)
        if used_fallback:
            return self._with_fallback_optimizer(
                fallback,
                "OpenAI response was not valid JSON.",
                raw_text,
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
            return self._parse_json(raw_text)
        except Exception as error:
            print(f"[OpenAIProvider] Warning: OpenAI request failed: {error}")
            return {}, str(error), True

    def _parse_json(self, raw_text):
        if isinstance(raw_text, dict):
            return raw_text, json.dumps(raw_text, ensure_ascii=False), False
        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                return parsed, raw_text, False
            return {}, raw_text, True
        except (TypeError, json.JSONDecodeError):
            return {}, raw_text, True

    def _with_fallback_reason(self, fallback, reason, raw_text=None):
        result = dict(fallback)
        result["mode"] = "openai_fallback"
        result["used_fallback"] = True
        result["fallback_reason"] = reason
        if raw_text is not None:
            result["raw_text"] = raw_text
        return result

    def _with_fallback_report(self, fallback, reason, raw_text=None):
        result = dict(fallback)
        result["mode"] = "openai_fallback"
        result["used_fallback"] = True
        result["reasoning_summary"] = reason
        if raw_text is not None:
            result["raw_text"] = raw_text
        return result

    def _with_fallback_optimizer(self, fallback, reason, raw_text=None):
        result = dict(fallback)
        report = dict(result.get("llm_optimizer_report") or {})
        report["mode"] = "openai_fallback"
        report["reason"] = reason
        report["used_fallback"] = True
        if raw_text is not None:
            report["raw_text"] = raw_text
        result["llm_optimizer_report"] = report
        return result

    def _list(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]
