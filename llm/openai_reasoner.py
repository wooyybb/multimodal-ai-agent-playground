import json
import os
import time

from llm.base_reasoner import BaseReasoner
from llm.json_parser import JSONParser


class OpenAIReasoner(BaseReasoner):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL") or "gpt-4.1-mini"
        self.parser = JSONParser()
        self.client = self._build_client()

    def reason(self, system_prompt: str, user_prompt: str) -> dict:
        started = time.perf_counter()
        if not self.client:
            return self._finish(
                {},
                started,
                used_fallback=True,
                parse_success=False,
                fallback_reason="OpenAI API key or client unavailable.",
            )

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            raw_text = getattr(response, "output_text", "") or str(response)
            parsed, failed = self.parser.parse(raw_text)
            return self._finish(
                parsed,
                started,
                used_fallback=bool(failed),
                parse_success=not failed,
                raw_text=raw_text if failed else "",
                fallback_reason="OpenAI response was not valid JSON." if failed else "",
            )
        except Exception as error:
            print(f"[OpenAIReasoner] Error: {error}")
            return self._finish(
                {},
                started,
                used_fallback=True,
                parse_success=False,
                raw_text=str(error),
                fallback_reason=str(error),
            )

    def _build_client(self):
        if not self.api_key:
            print("[OpenAIReasoner] Warning: OPENAI_API_KEY missing. Rule fallback will be used.")
            return None
        try:
            from openai import OpenAI

            return OpenAI(api_key=self.api_key)
        except Exception as error:
            print(f"[OpenAIReasoner] Warning: OpenAI client unavailable: {error}")
            return None

    def _finish(
        self,
        result,
        started,
        *,
        used_fallback,
        parse_success,
        raw_text="",
        fallback_reason="",
    ):
        latency = round(time.perf_counter() - started, 4)
        print(f"[LLM Layer] Provider: openai")
        print(f"[LLM Layer] Used fallback: {bool(used_fallback)}")
        print(f"[LLM Layer] JSON parse success: {bool(parse_success)}")
        print(f"[LLM Layer] Reasoning latency: {latency}s")
        output = dict(result or {})
        output["used_fallback"] = bool(used_fallback)
        output["llm_provider"] = "openai"
        output["llm_used_fallback"] = bool(used_fallback)
        output["llm_json_parse_success"] = bool(parse_success)
        output["llm_reasoning_latency"] = latency
        if raw_text:
            output["raw_text"] = raw_text
            output["llm_reasoning_raw_text"] = raw_text
        if fallback_reason:
            output["fallback_reason"] = fallback_reason
        return output


def dumps_payload(payload: dict) -> str:
    return json.dumps(payload or {}, ensure_ascii=False, indent=2)
