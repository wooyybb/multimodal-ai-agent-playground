class PromptAssembler:
    def run(
        self,
        state_or_caption,
        user_prompt=None,
        character_section=None,
        style_section=None,
        layout_section=None,
        pose_section=None,
        expression_section=None,
        negative_section=None,
        scene_plan=None,
        compressed_context=None,
        lighting_section=None,
    ) -> dict:
        if isinstance(state_or_caption, dict):
            state = state_or_caption
            result = self._run_legacy(
                state.get("caption", ""),
                state.get("user_prompt", ""),
                state.get("character_section", {}),
                state.get("style_section", {}),
                state.get("layout_section", {}),
                state.get("pose_section", {}),
                state.get("expression_section", {}),
                state.get("negative_section", {}),
                scene_plan=state.get("scene_plan"),
                compressed_context=state.get("compressed_context", {}),
                lighting_section=state.get("lighting_section", {}),
                context_program=state.get("context_program"),
            )
            return {
                "canonical_prompt": result.get("canonical_prompt", ""),
                "final_prompt": result.get(
                    "canonical_prompt",
                    result.get("generation_prompt", ""),
                ),
                "negative_prompt": result.get("negative_prompt"),
                "prompt_sections": result.get("prompt_sections", {}),
            }

        return self._run_legacy(
            state_or_caption,
            user_prompt,
            character_section,
            style_section,
            layout_section,
            pose_section,
            expression_section,
            negative_section,
            scene_plan=scene_plan,
            compressed_context=compressed_context,
            lighting_section=lighting_section,
        )

    def _run_legacy(
        self,
        caption,
        user_prompt,
        character_section,
        style_section,
        layout_section,
        pose_section,
        expression_section,
        negative_section,
        scene_plan=None,
        compressed_context=None,
        lighting_section=None,
        context_program=None,
    ) -> dict:
        print("[PromptAssembler] Building generation prompt...")
        if context_program:
            print("[PromptAssembler] Reading context program...")
        print("[PromptAssembler] Adding character preservation rules...")
        if scene_plan:
            print("[PromptAssembler] Adding scene plan...")

        if context_program:
            visual = self._visual_from_context_program(context_program, caption)
            character_bits = visual["character"]
            scene_bits = visual["scene"]
            style_bits = visual["style"]
            rendering_bits = visual["rendering"]
            layout_bits = visual["layout"]
            pose_bits = visual["pose"]
            expression_bits = visual["expression"]
            lighting_bits = visual["lighting"]
            retrieved_lighting = visual["retrieved_lighting"]
            negative_prompt = ", ".join(visual["negative"])
        else:
            character_bits = self._character_prompt_bits(character_section, caption)
            scene_bits = self._scene_prompt_bits(scene_plan)
            style_bits = (style_section or {}).get("style_keywords", [])
            rendering_bits = (style_section or {}).get("rendering_rules", [])
            layout_bits = self._layout_prompt_bits(layout_section)
            pose_bits = (pose_section or {}).get("pose_rules", [])
            expression_bits = (expression_section or {}).get("expression_rules", [])
            lighting_bits = self._lighting_prompt_bits(lighting_section)
            retrieved_lighting = (compressed_context or {}).get("retrieved_lighting_hint")
            negative_prompt = ", ".join((negative_section or {}).get("negative_prompt", []))

        parts = [
            "high quality",
            f"detailed image of {caption}",
            ", ".join(scene_bits),
            ", ".join(character_bits),
            ", ".join(style_bits),
            ", ".join(rendering_bits),
            ", ".join(layout_bits),
            ", ".join(pose_bits),
            ", ".join(expression_bits),
            ", ".join(lighting_bits),
            retrieved_lighting,
        ]

        if user_prompt and str(user_prompt).strip():
            parts.append(f"user request: {str(user_prompt).strip()}")

        generation_prompt = ", ".join(part for part in parts if part)
        generation_prompt = self._limit_words(generation_prompt, max_words=120)

        result = {
            "canonical_prompt": generation_prompt,
            "generation_prompt": generation_prompt,
            "negative_prompt": negative_prompt,
            "prompt_sections": {
                "character": character_section,
                "style": style_section,
                "layout": layout_section,
                "pose": pose_section,
                "expression": expression_section,
                "lighting": lighting_section,
                "negative": negative_section,
                "scene": scene_plan,
                "context_program_summary": (
                    self._context_summary(context_program) if context_program else None
                ),
            },
        }
        print(f"[PromptAssembler] Generation prompt: {generation_prompt}")
        print(f"[PromptAssembler] Negative prompt: {negative_prompt}")
        return result

    def _limit_words(self, prompt, max_words):
        words = prompt.split()
        if len(words) <= max_words:
            return prompt
        return " ".join(words[:max_words]).rstrip(" ,.")

    def _dict_values(self, section):
        values = []
        for value in (section or {}).values():
            if isinstance(value, list):
                values.extend(value)
            elif value:
                values.append(str(value))
        return values

    def _layout_prompt_bits(self, layout_section):
        if not layout_section:
            return []

        layout_type = layout_section.get("layout_type")
        aspect_ratio = layout_section.get("aspect_ratio")
        frame_structure = layout_section.get("frame_structure")
        camera_view = layout_section.get("camera_view")
        subject_placement = layout_section.get("subject_placement")
        background_style = layout_section.get("background_style")
        composition_rules = layout_section.get("composition_rules") or []

        layout_phrase = self._layout_type_phrase(layout_type)
        camera_phrase = self._camera_phrase(camera_view)
        placement_phrase = self._placement_phrase(subject_placement)

        bits = [
            layout_phrase,
            aspect_ratio,
            frame_structure,
            camera_phrase,
            placement_phrase,
            background_style,
            ", ".join(composition_rules[:4]),
        ]
        return [bit for bit in bits if bit]

    def _layout_type_phrase(self, layout_type):
        phrases = {
            "photobooth": "vertical Korean photobooth strip",
            "scrapbook": "scrapbook-style page layout",
            "poster": "clean poster composition",
            "profile": "profile portrait layout",
            "portrait": "portrait composition",
            "illustration": "illustration-focused composition",
            "sticker_sheet": "sticker sheet layout",
            "concept_sheet": "concept sheet layout",
            "comic_page": "comic page layout",
            "cinematic": "cinematic scene composition",
        }
        return phrases.get(layout_type, "balanced image composition")

    def _camera_phrase(self, camera_view):
        phrases = {
            "front": "front-facing camera",
            "eye_level": "eye-level view",
            "slightly_above": "slightly above camera angle",
            "wide": "wide camera view",
            "close_up": "close-up view",
            "medium": "medium shot",
            "full_body": "full-body view",
            "half_body": "half-body view",
        }
        return phrases.get(camera_view, camera_view)

    def _placement_phrase(self, subject_placement):
        phrases = {
            "centered": "centered subject placement",
            "rule_of_thirds": "rule-of-thirds composition",
            "symmetrical": "symmetrical subject placement",
            "diagonal": "diagonal visual flow",
            "balanced": "balanced centered composition",
        }
        return phrases.get(subject_placement, subject_placement)

    def _character_prompt_bits(self, character_section, caption):
        if not character_section:
            return [str(caption or "main character")]

        characters = character_section.get("characters") or []
        if not characters:
            return [str(caption or "main character")]

        character_count = character_section.get("character_count", len(characters))
        if character_count > 1:
            intro = f"{character_count} separate recognizable characters"
        else:
            intro = "one recognizable character"

        caption_hints = [
            character.get("caption_hint")
            for character in characters
            if character.get("caption_hint")
        ]
        preservation = (
            "use uploaded screenshots as character references, each reference image "
            "represents one separate character, do not merge characters, preserve "
            "each character's outfit, hairstyle, silhouette, proportions, visual "
            "vibe, and color balance"
        )
        recognizable = "keep each character immediately recognizable from the reference"

        return [intro, ", ".join(caption_hints[:3]), preservation, recognizable]

    def _scene_prompt_bits(self, scene_plan):
        if not scene_plan:
            return []
        narrative = scene_plan.get("narrative")
        camera_intent = scene_plan.get("camera_intent")
        scene_rules = scene_plan.get("scene_rules") or []
        bits = [narrative, camera_intent, ", ".join(scene_rules[:3])]
        return [bit for bit in bits if bit]

    def _lighting_prompt_bits(self, lighting_section):
        if not lighting_section:
            return []
        values = []
        for value in lighting_section.values():
            if isinstance(value, list):
                values.extend(str(item) for item in value if item)
            elif value:
                values.append(str(value))
        return values

    def _visual_from_context_program(self, context_program, caption):
        scene = context_program.get("scene") or {}
        characters = context_program.get("characters") or {}
        style = context_program.get("style") or {}
        layout = context_program.get("layout") or {}
        pose = context_program.get("pose") or {}
        expression = context_program.get("expression") or {}
        lighting = context_program.get("lighting") or {}
        quality = context_program.get("quality") or {}
        negative = context_program.get("negative") or {}
        retrieval = context_program.get("retrieval") or {}

        layout_section = {
            "layout_type": layout.get("layout_type"),
            "aspect_ratio": layout.get("aspect_ratio"),
            "frame_structure": layout.get("frame_structure"),
            "camera_view": layout.get("camera_view"),
            "subject_placement": layout.get("subject_placement"),
            "composition_rules": layout.get("composition_rules", []),
        }

        character_bits = [
            f"{characters.get('character_count', 1) or 1} recognizable character",
            ", ".join(
                str(item)
                for item in characters.get("preservation_rules", [])[:3]
            ),
            str(caption or "main subject"),
        ]

        return {
            "scene": self._clean_bits([
                scene.get("narrative"),
                scene.get("camera_intent"),
                scene.get("interaction"),
            ]),
            "character": [bit for bit in character_bits if bit],
            "style": self._clean_bits(style.get("style_keywords", [])),
            "rendering": (
                self._clean_bits(style.get("rendering_rules", []))
                + self._clean_bits(quality.get("quality_keywords", []))
            ),
            "layout": self._layout_prompt_bits(layout_section),
            "pose": self._clean_bits(pose.get("pose_rules", [])),
            "expression": self._clean_bits(expression.get("expression_rules", [])),
            "lighting": self._clean_bits(lighting.get("lighting_keywords", [])),
            "retrieved_lighting": retrieval.get("retrieved_lighting"),
            "negative": (
                self._clean_bits(negative.get("negative_prompt", []))
                + self._clean_bits(negative.get("strict_avoid", []))
            ),
        }

    def _context_summary(self, context_program):
        scene = context_program.get("scene") or {}
        layout = context_program.get("layout") or {}
        provider = context_program.get("provider") or {}
        return {
            "scene_type": scene.get("scene_type"),
            "layout_type": layout.get("layout_type"),
            "provider": provider.get("selected_provider"),
        }

    def _clean_bits(self, values):
        return [str(value) for value in (values or []) if value]
