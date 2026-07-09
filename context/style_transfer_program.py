import re

from context.style_transfer_schema import StyleTransferSchema


class StyleTransferProgramBuilder:
    PHOTObooth_KEYWORDS = (
        "인생네컷",
        "포토이즘",
        "photobooth",
        "memory collage",
        "4 frames",
        "sticker photo",
    )
    BAD_CUTE_KEYWORDS = (
        "intentionally bad but cute",
        "ms paint",
        "rough scribbles",
        "ugly-cute",
        "childish lineart",
    )
    WEAPON_TERMS = (
        "weapon",
        "weapons",
        "sword",
        "blade",
        "combat stance",
        "action scene",
        "weapon showcase",
        "holding a sword",
    )
    FORBIDDEN_MARKERS = (
        "remove",
        "avoid",
        "forbidden",
        "do not",
        "strictly avoid",
        "no ",
    )

    def build(self, state: dict) -> dict:
        state = state or {}
        user_prompt = str(state.get("user_prompt") or "")
        caption = str(state.get("caption") or "")
        forbidden = self._extract_forbidden(user_prompt)
        program = self._base_program()

        if self._contains(user_prompt, self.PHOTObooth_KEYWORDS):
            self._apply_photobooth_preset(program)
        if self._contains(user_prompt, self.BAD_CUTE_KEYWORDS):
            self._apply_bad_cute_preset(program)

        program["forbidden_concepts"] = forbidden
        program["negative_prompt"] = self._negative_prompt(forbidden)
        program["source_summary"] = {
            "user_prompt": user_prompt,
            "caption": caption,
            "presets": self._detected_presets(user_prompt),
        }
        planner_program = (state.get("planner_result") or {}).get(
            "style_transfer_program"
        )
        if planner_program:
            program = StyleTransferSchema().to_legacy_program(
                planner_program,
                program,
            )
            program["requirement_parser"] = (state.get("planner_result") or {}).get(
                "requirement_parser",
                {},
            )
            program["source_summary"]["requirement_parser_used"] = True
        return program

    def _base_program(self):
        return {
            "task_type": "reference_aware_style_transfer",
            "character_count": 1,
            "character_rules": {
                "preserve_identity": True,
                "preserve_outfit": True,
                "preserve_hairstyle": True,
                "preserve_silhouette": True,
                "do_not_merge_characters": True,
            },
            "style": {
                "name": "",
                "rendering": "",
                "mood": "",
                "color_palette": [],
                "texture": "",
            },
            "layout": {
                "format": "",
                "structure": "",
                "background": "",
                "decorations": [],
            },
            "pose_expression": {
                "allowed": [],
                "forbidden": [],
            },
            "forbidden_concepts": [],
            "negative_prompt": [],
            "text_rules": {
                "allow_small_text": True,
                "avoid_large_typography": True,
                "language_constraints": [],
            },
        }

    def _apply_photobooth_preset(self, program):
        program["layout"].update(
            {
                "format": "vertical 9:16",
                "structure": "four connected vertical photobooth frames",
                "background": "white paper / soft pastel scrapbook",
                "decorations": ["small stickers", "memory collage accents"],
            }
        )
        program["style"].update(
            {
                "name": "soft Korean webtoon photobooth",
                "mood": "natural, warm, candid, relaxed",
            }
        )

    def _apply_bad_cute_preset(self, program):
        program["style"].update(
            {
                "name": "ugly-cute rough hand-drawn",
                "rendering": (
                    "MS Paint mouse drawing aesthetic, rough scribbles, "
                    "childish lineart"
                ),
                "texture": "messy coloring, visible pen strokes, rough marker coloring",
            }
        )
        program["layout"]["background"] = "white empty background"

    def _extract_forbidden(self, user_prompt):
        text = user_prompt.lower()
        forbidden = []
        if any(marker in text for marker in self.FORBIDDEN_MARKERS):
            for term in self.WEAPON_TERMS:
                if any(word in text for word in ("weapon", "sword", "blade")):
                    forbidden.append(term)

        marker_pattern = r"(?:remove|avoid|forbidden|do not|strictly avoid|no)\s+([^,.]+)"
        for match in re.finditer(marker_pattern, text):
            phrase = " ".join(match.group(1).split()).strip()
            if phrase:
                forbidden.append(phrase)

        return self._unique(forbidden)

    def _negative_prompt(self, forbidden):
        base = ["low quality", "blurry", "bad anatomy", "duplicate subject"]
        return self._unique(base + list(forbidden or []))

    def _detected_presets(self, user_prompt):
        presets = []
        if self._contains(user_prompt, self.PHOTObooth_KEYWORDS):
            presets.append("korean_photobooth")
        if self._contains(user_prompt, self.BAD_CUTE_KEYWORDS):
            presets.append("bad_cute_ms_paint")
        return presets

    def _contains(self, text, keywords):
        lowered = str(text or "").lower()
        return any(keyword.lower() in lowered for keyword in keywords)

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
