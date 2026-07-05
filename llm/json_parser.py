import json
import re


class JSONParser:
    def parse(self, text) -> tuple[dict, bool]:
        if isinstance(text, dict):
            return text, False
        raw_text = str(text or "").strip()
        if not raw_text:
            return {}, True

        cleaned = self._strip_code_fence(raw_text)
        for candidate in (cleaned, self._extract_json_object(cleaned)):
            if not candidate:
                continue
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed, False
            except json.JSONDecodeError:
                continue
        return {"raw_text": raw_text}, True

    def _strip_code_fence(self, text):
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()
        return cleaned

    def _extract_json_object(self, text):
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return ""
        return text[start : end + 1]
