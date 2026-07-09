import json
import os
import re

from llm.openai_reasoner import dumps_payload
from llm.reasoner_router import ReasonerRouter


class RequirementParser:
    """Parse long user requirements into Style Transfer Program JSON.

    This parser never returns a final image prompt. It only returns structured
    planning data that downstream context and provider prompt compilers render.
    """

    DEFAULT_MODEL = "gpt-5-mini"

    def __init__(self, reasoner_router=None):
        self.provider = str(os.getenv("LLM_PROVIDER", "rule") or "rule").lower()
        os.environ.setdefault("OPENAI_MODEL", self.DEFAULT_MODEL)
        self.reasoner_router = reasoner_router or ReasonerRouter(self.provider)

    def parse(self, payload: dict) -> dict:
        payload = payload or {}
        fallback_program = self._rule_program(payload)
        if self.provider in ("rule", "mock", "none", ""):
            return self._result(
                fallback_program,
                provider="rule",
                used_fallback=True,
                reason="rule mode",
            )

        result = self.reasoner_router.reason(
            self._system_prompt(),
            dumps_payload(self._payload(payload)),
            fallback=fallback_program,
            schema_name="requirement_parser_style_transfer_program",
        )
        used_fallback = bool(result.get("reasoning_used_fallback"))
        if used_fallback:
            return self._result(
                fallback_program,
                provider=result.get("reasoning_provider", self.provider),
                used_fallback=True,
                reason=result.get("reasoning_fallback_reason")
                or result.get("fallback_reason")
                or "LLM parser fallback",
                raw_text=result.get("llm_reasoning_raw_text", ""),
            )

        program = self._normalize_program(result, fallback_program)
        return self._result(
            program,
            provider=result.get("reasoning_provider", self.provider),
            used_fallback=False,
            reason="",
            raw_text=result.get("llm_reasoning_raw_text", ""),
        )

    def _payload(self, payload):
        return {
            "user_long_prompt": payload.get("user_long_prompt")
            or payload.get("user_prompt"),
            "vision_result": payload.get("vision_result"),
            "reference_image_parser_result": payload.get("reference_image")
            or payload.get("reference_image_parser_result"),
            "character_program": payload.get("character_program"),
            "existing_style_transfer_program": payload.get(
                "existing_style_transfer_program"
            )
            or payload.get("style_transfer_program"),
        }

    def _system_prompt(self):
        return (
            "You are the Requirement Parser inside a Planning Agent for a "
            "reference-aware style transfer framework. Return JSON only. "
            "Do not write a final image prompt. Convert the user requirement "
            "into a Style Transfer Program with keys: task, identity, style, "
            "layout, pose_expression, text_rules, negative, "
            "generation_strategy, reasoning_summary. User remove/avoid/do not "
            "instructions must be placed in negative.remove and must override "
            "reference image captions."
        )

    def _rule_program(self, payload):
        text = str(payload.get("user_long_prompt") or payload.get("user_prompt") or "")
        lowered = text.lower()
        remove = self._extract_negative(text)
        style = self._style_from_text(lowered)
        layout = self._layout_from_text(lowered)
        generation_strategy = {
            "provider": "sdxl_quality",
            "use_img2img": True,
            "use_ip_adapter": True,
            "use_controlnet": "controlnet" in lowered or "pose" in lowered,
            "identity_strength": 0.8,
            "style_strength": self._style_strength(lowered),
            "structure_strength": 0.5,
        }
        return {
            "task": {
                "type": "reference_aware_style_transfer",
                "goal": text[:300],
            },
            "identity": {
                "preserve_identity": True,
                "preserve_outfit": True,
                "preserve_hairstyle": True,
                "preserve_palette": True,
                "do_not_merge_characters": True,
            },
            "style": style,
            "layout": layout,
            "pose_expression": {
                "interaction": "",
                "energy": "natural",
                "naturalness": "preserve natural pose",
                "allowed": [],
                "forbidden": remove,
            },
            "text_rules": {
                "allow_text": True,
                "text_amount": "minimal",
                "language": self._language(lowered),
                "typography": "small handwritten",
            },
            "negative": {
                "remove": remove,
            },
            "generation_strategy": generation_strategy,
            "reasoning_summary": (
                "Rule parser converted the user requirement into structured "
                "style transfer fields."
            ),
        }

    def _style_from_text(self, lowered):
        style = {
            "name": "",
            "renderer": "",
            "lineart": "",
            "lighting": "",
            "palette": "",
            "texture": "",
            "mood": "",
        }
        if any(term in lowered for term in ("anime", "webtoon", "manga")):
            style.update(
                {
                    "name": "anime webtoon",
                    "renderer": "clean anime illustration",
                    "lineart": "clean expressive lineart",
                    "lighting": "soft cel-shaded lighting",
                    "mood": "expressive and polished",
                }
            )
        if any(term in lowered for term in ("photobooth", "photoism", "인생네컷", "포토이즘")):
            style.update(
                {
                    "name": "soft photobooth webtoon",
                    "renderer": "soft Korean webtoon",
                    "lighting": "gentle studio lighting",
                    "palette": "pastel paper colors",
                    "mood": "warm candid memory",
                }
            )
        if any(term in lowered for term in ("ms paint", "ugly-cute", "childish", "scribble")):
            style.update(
                {
                    "name": "ugly-cute rough drawing",
                    "renderer": "MS Paint mouse drawing",
                    "lineart": "childish uneven lineart",
                    "texture": "rough scribbles and messy coloring",
                    "mood": "intentionally awkward but cute",
                }
            )
        if any(term in lowered for term in ("realistic", "photo-realistic", "photorealistic")):
            style.update(
                {
                    "name": "realistic preserve",
                    "renderer": "realistic illustration",
                    "lighting": "natural lighting",
                    "mood": "faithful and polished",
                }
            )
        return style

    def _layout_from_text(self, lowered):
        layout = {
            "format": "",
            "composition": "",
            "panel_type": "",
            "panel_count": 0,
            "background": "",
            "decorations": [],
        }
        if any(term in lowered for term in ("photobooth", "인생네컷", "4 frame", "four frame")):
            layout.update(
                {
                    "format": "vertical 9:16",
                    "composition": "four connected vertical frames",
                    "panel_type": "photobooth strip",
                    "panel_count": 4,
                    "background": "white paper or soft pastel scrapbook",
                    "decorations": ["small stickers", "memory collage accents"],
                }
            )
        return layout

    def _extract_negative(self, text):
        lowered = text.lower()
        values = []
        marker_pattern = r"(?:remove|avoid|forbidden|do not|strictly avoid|no)\s+([^,.]+)"
        for match in re.finditer(marker_pattern, lowered):
            phrase = " ".join(match.group(1).split()).strip()
            if phrase:
                values.append(phrase)
        if any(word in lowered for word in ("remove weapon", "avoid weapon", "no weapon")):
            values.extend(["weapon", "sword", "blade", "combat stance"])
        return self._unique(values)

    def _style_strength(self, lowered):
        if any(term in lowered for term in ("strong style", "dramatic", "completely transform")):
            return 0.75
        if any(term in lowered for term in ("subtle", "slight", "preserve")):
            return 0.45
        return 0.6

    def _language(self, lowered):
        if any(term in lowered for term in ("korean", "hangul", "한글", "한국어")):
            return "korean"
        if "english" in lowered:
            return "english"
        return ""

    def _normalize_program(self, candidate, fallback):
        output = json.loads(json.dumps(fallback))
        candidate = candidate or {}
        for key in (
            "task",
            "identity",
            "style",
            "layout",
            "pose_expression",
            "text_rules",
            "negative",
            "generation_strategy",
        ):
            value = candidate.get(key)
            if isinstance(value, dict):
                merged = dict(output.get(key) or {})
                merged.update({k: v for k, v in value.items() if v not in (None, "")})
                output[key] = merged
        if candidate.get("reasoning_summary"):
            output["reasoning_summary"] = str(candidate.get("reasoning_summary"))
        output["task"]["type"] = "reference_aware_style_transfer"
        output.setdefault("negative", {}).setdefault("remove", [])
        return output

    def _result(self, program, provider, used_fallback, reason, raw_text=""):
        return {
            "style_transfer_program": program,
            "requirement_parser": {
                "enabled": provider not in ("rule", "mock", "none", ""),
                "provider": provider,
                "used_fallback": bool(used_fallback),
                "error": reason if used_fallback and reason != "rule mode" else "",
                "raw_text": raw_text,
                "reasoning_summary": program.get("reasoning_summary", ""),
            },
            "parser_provider": provider,
            "parser_used_fallback": bool(used_fallback),
            "parser_error": reason if used_fallback and reason != "rule mode" else "",
            "llm_raw_text": raw_text,
            "reasoning_summary": program.get("reasoning_summary", ""),
        }

    def _unique(self, values):
        unique = []
        seen = set()
        for value in values:
            item = str(value or "").strip(" ,.")
            key = item.lower()
            if item and key not in seen:
                unique.append(item)
                seen.add(key)
        return unique
