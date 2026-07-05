import json
import os

from llm.base_reasoner import BaseReasoner
from llm.json_parser import JSONParser


class OpenAIReasoner(BaseReasoner):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.5")
        self.parser = JSONParser()
        self.client = self._build_client()

    def reason(self, system_prompt: str, user_prompt: str) -> dict:
        if not self.client:
            return {
                "used_fallback": True,
                "fallback_reason": "OpenAI API key or client unavailable.",
            }

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
            parsed["used_fallback"] = bool(failed)
            if failed:
                parsed["fallback_reason"] = "OpenAI response was not valid JSON."
            return parsed
        except Exception as error:
            print(f"[OpenAIReasoner] Error: {error}")
            return {
                "used_fallback": True,
                "fallback_reason": str(error),
            }

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


def dumps_payload(payload: dict) -> str:
    return json.dumps(payload or {}, ensure_ascii=False, indent=2)
