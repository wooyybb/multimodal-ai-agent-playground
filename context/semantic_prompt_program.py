from context.conflict_resolver import ConflictResolver
from context.semantic_merge import SemanticMerge


class SemanticPromptProgramBuilder:
    SECTIONS = (
        "identity",
        "style",
        "layout",
        "scene",
        "lighting",
        "quality",
        "negative",
        "constraints",
    )

    def build(
        self,
        prompt_blocks: dict,
        style_transfer_program: dict | None = None,
        forbidden_concepts=None,
    ) -> dict:
        style_transfer_program = style_transfer_program or {}
        forbidden_concepts = list(
            forbidden_concepts
            or style_transfer_program.get("forbidden_concepts")
            or []
        )
        program = {
            "identity": self._list(prompt_blocks.get("subject")),
            "style": self._style(prompt_blocks, style_transfer_program),
            "layout": self._layout(prompt_blocks, style_transfer_program),
            "scene": self._list(prompt_blocks.get("scene")),
            "lighting": self._list(prompt_blocks.get("lighting")),
            "quality": self._list(prompt_blocks.get("quality")),
            "negative": self._negative(style_transfer_program),
            "constraints": {
                "forbidden_concepts": forbidden_concepts,
                "user_intent_priority": True,
            },
        }
        merged_program, merge_report = SemanticMerge().merge_program(program)
        resolved_program, conflict_report = ConflictResolver().resolve(
            merged_program,
            forbidden_concepts=forbidden_concepts,
        )
        return {
            "semantic_prompt_program": resolved_program,
            "semantic_merge_report": merge_report,
            "conflict_resolution_report": conflict_report,
        }

    def _style(self, prompt_blocks, style_transfer_program):
        style = style_transfer_program.get("style") or {}
        values = [
            prompt_blocks.get("style"),
            style.get("name"),
            style.get("rendering"),
            style.get("mood"),
            style.get("color_palette", []),
            style.get("texture"),
        ]
        return self._list(values)

    def _layout(self, prompt_blocks, style_transfer_program):
        layout = style_transfer_program.get("layout") or {}
        values = [
            prompt_blocks.get("layout"),
            layout.get("format"),
            layout.get("structure"),
            layout.get("background"),
            layout.get("decorations", []),
        ]
        return self._list(values)

    def _negative(self, style_transfer_program):
        return self._list(style_transfer_program.get("negative_prompt", []))

    def _list(self, value):
        values = []
        self._append(values, value)
        result = []
        seen = set()
        for item in values:
            text = str(item or "").strip(" ,.")
            key = text.lower()
            if text and key not in seen:
                result.append(text)
                seen.add(key)
        return result

    def _append(self, values, value):
        if value is None:
            return
        if isinstance(value, str):
            for part in value.split(","):
                if part.strip():
                    values.append(part.strip())
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                self._append(values, item)
            return
        if isinstance(value, dict):
            for item in value.values():
                self._append(values, item)
            return
        values.append(value)
