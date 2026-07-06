from generation.reference_conditioning import ReferenceConditioningBuilder
from modules.planning.llm_style_transfer_planner import LLMStyleTransferPlanner
from context.provider_renderer import ProviderRenderer
from context.prompt_sanitizer import PromptSanitizer
from context.prompt_validator import PromptValidator
from context.semantic_prompt_program import SemanticPromptProgramBuilder
from context.style_transfer_program import StyleTransferProgramBuilder


class PromptCompiler:
    INTERNAL_TERMS = (
        "context_program",
        "agent trace",
        "debug",
        "internal context",
        "prompt quality score",
    )
    CLIP_REMOVE_TERMS = (
        "masterpiece",
        "8k",
        "ultra detailed",
        "ultra-detailed",
        "best quality",
        "high quality",
        "low quality",
        "negative",
        "bad anatomy",
        "blurry",
    )

    def run(self, state: dict) -> dict:
        print("[PromptCompiler] Running...")
        state = state or {}
        provider = self._provider(state)
        context_program = state.get("context_program") or {}
        context_reasoning = state.get("context_reasoning") or {}
        context_validation = state.get("context_validation") or {}
        prompt_sections = state.get("prompt_sections") or {}
        negative_prompt = state.get("negative_prompt") or ""
        rule_style_transfer_program = StyleTransferProgramBuilder().build(state)
        planner_state = dict(state)
        planner_state["style_transfer_program"] = rule_style_transfer_program
        llm_style_result = LLMStyleTransferPlanner().run(planner_state)
        style_transfer_program = llm_style_result.get(
            "final_style_transfer_program",
            rule_style_transfer_program,
        )
        forbidden_concepts = style_transfer_program.get("forbidden_concepts", [])
        sanitizer = PromptSanitizer()

        print(f"[PromptCompiler] Provider: {provider}")
        print(f"[PromptCompiler] Forbidden concepts: {forbidden_concepts}")
        prompt_blocks = self._build_prompt_blocks(
            context_program,
            context_reasoning,
            prompt_sections,
        )
        self._apply_style_transfer_program(prompt_blocks, style_transfer_program)
        semantic_result = SemanticPromptProgramBuilder().build(
            prompt_blocks,
            style_transfer_program=style_transfer_program,
            forbidden_concepts=forbidden_concepts,
        )
        semantic_program = semantic_result["semantic_prompt_program"]
        provider_rendering = ProviderRenderer().render(semantic_program, provider)
        negative = sanitizer.merge_negative_prompt(
            self._negative_prompt(context_program, negative_prompt),
            provider_rendering.get("negative_prompt")
            or style_transfer_program.get("negative_prompt", []),
        )

        if provider == "gpt_image":
            generation_prompt, notes, target_words = self._compile_gpt_image(prompt_blocks)
        elif provider in {"sdxl", "sdxl_quality"}:
            generation_prompt = provider_rendering["generation_prompt"]
            notes, target_words = ["rendered SDXL prompt from semantic program"], 60
        else:
            generation_prompt = provider_rendering["generation_prompt"]
            notes, target_words = ["rendered dense FLUX prompt from semantic program"], 100
            provider = "flux"

        if context_validation and context_validation.get("valid") is False:
            notes.append("context validation reported invalid context")
        if negative and provider == "flux":
            notes.append("negative prompt preserved in package but not directly used by FLUX generation")

        rendered_prompts = self._render_prompts(
            generation_prompt,
            negative,
            prompt_blocks,
            context_program,
            context_reasoning,
            style_transfer_program,
            provider,
            sanitizer,
            forbidden_concepts,
            provider_rendering,
        )
        sanitizer_report = rendered_prompts.pop("prompt_sanitizer_report")
        validation_report = PromptValidator().validate(
            rendered_prompts,
            style_transfer_program=style_transfer_program,
            forbidden_concepts=forbidden_concepts,
        )
        reference_conditioning = ReferenceConditioningBuilder().build(state)
        package = {
            "provider": provider,
            "positive_prompt": rendered_prompts["generation_prompt"],
            "negative_prompt": rendered_prompts["negative_prompt"],
            "prompt_blocks": prompt_blocks,
            "prompt_rendering": rendered_prompts,
            "style_transfer_program": style_transfer_program,
            "llm_style_transfer_program": llm_style_result.get(
                "llm_style_transfer_program"
            ),
            "llm_used_fallback": llm_style_result.get("llm_used_fallback"),
            "llm_reasoning_summary": llm_style_result.get("llm_reasoning_summary"),
            "final_style_transfer_program": style_transfer_program,
            "generation_strategy": llm_style_result.get("generation_strategy", {}),
            "semantic_prompt_program": semantic_program,
            "semantic_merge_report": semantic_result["semantic_merge_report"],
            "conflict_resolution_report": semantic_result[
                "conflict_resolution_report"
            ],
            "provider_render_report": provider_rendering.get("provider_render_report"),
            "prompt_sanitizer_report": sanitizer_report,
            "prompt_validation_report": validation_report,
            "reference_conditioning_package": reference_conditioning,
            "compiler_notes": notes,
            "prompt_budget": {
                "target_words": target_words,
                "actual_words": len(rendered_prompts["generation_prompt"].split()),
            },
        }

        print(f"[PromptCompiler] Positive prompt word count: {package['prompt_budget']['actual_words']}")
        print(f"[PromptCompiler] CLIP prompt word count: {len(rendered_prompts['clip_prompt'].split())}")
        print(f"[PromptCompiler] Compiler notes: {notes}")
        return {
            "compiled_prompt_package": package,
            "reference_conditioning_package": reference_conditioning,
            "style_transfer_program": style_transfer_program,
            "llm_style_transfer_program": llm_style_result.get(
                "llm_style_transfer_program"
            ),
            "llm_style_transfer_metadata": llm_style_result.get(
                "llm_style_transfer_metadata",
                {},
            ),
            "llm_used_fallback": llm_style_result.get("llm_used_fallback"),
            "llm_reasoning_summary": llm_style_result.get("llm_reasoning_summary"),
            "final_style_transfer_program": style_transfer_program,
            "generation_strategy": llm_style_result.get("generation_strategy", {}),
            "forbidden_concepts": forbidden_concepts,
            "semantic_prompt_program": semantic_program,
            "semantic_merge_report": semantic_result["semantic_merge_report"],
            "conflict_resolution_report": semantic_result[
                "conflict_resolution_report"
            ],
            "provider_render_report": provider_rendering.get("provider_render_report"),
            "prompt_sanitizer_report": sanitizer_report,
            "prompt_validation_report": validation_report,
            "prompt_rendering": rendered_prompts,
            **rendered_prompts,
        }

    def _provider(self, state):
        routing = state.get("provider_routing") or {}
        return str(
            state.get("generation_provider")
            or (state.get("generation_plan") or {}).get("provider")
            or state.get("provider")
            or routing.get("selected_provider")
            or routing.get("fallback_provider")
            or "flux"
        ).lower()

    def _build_prompt_blocks(self, context_program, context_reasoning, prompt_sections):
        scene = context_program.get("scene") or {}
        characters = context_program.get("characters") or {}
        style = context_program.get("style") or {}
        layout = context_program.get("layout") or {}
        pose = context_program.get("pose") or {}
        expression = context_program.get("expression") or {}
        lighting = context_program.get("lighting") or {}
        quality = context_program.get("quality") or {}

        return {
            "subject": self._join_parts(
                [
                    self._character_phrase(characters),
                    (prompt_sections.get("character") or {}).get("summary"),
                ]
            ),
            "scene": self._join_parts(
                [
                    scene.get("narrative"),
                    scene.get("interaction"),
                    context_reasoning.get("scene_goal"),
                    context_reasoning.get("interaction_goal"),
                ]
            ),
            "style": self._join_parts(
                [
                    style.get("style_keywords", []),
                    style.get("rendering_rules", []),
                    context_reasoning.get("style_goal"),
                ]
            ),
            "layout": self._join_parts(
                [
                    layout.get("layout_type"),
                    layout.get("aspect_ratio"),
                    layout.get("frame_structure"),
                    layout.get("camera_view"),
                    layout.get("subject_placement"),
                    layout.get("composition_rules", []),
                    context_reasoning.get("composition_goal"),
                ]
            ),
            "lighting": self._join_parts(
                [
                    lighting.get("lighting_keywords", []),
                    lighting.get("mood"),
                ]
            ),
            "quality": self._join_parts(
                [
                    quality.get("quality_keywords", []),
                    pose.get("pose_rules", []),
                    expression.get("expression_rules", []),
                ]
            ),
        }

    def _compile_flux(self, prompt_blocks):
        prompt = self._join_parts(
            [
                prompt_blocks.get("subject"),
                prompt_blocks.get("scene"),
                prompt_blocks.get("style"),
                prompt_blocks.get("layout"),
                prompt_blocks.get("lighting"),
                prompt_blocks.get("quality"),
            ]
        )
        prompt = self._clean_prompt(prompt)
        prompt = self._limit_words(prompt, 110)
        return prompt, ["compiled dense FLUX visual prompt"], 100

    def _compile_sdxl(self, prompt_blocks, style_transfer_program):
        prompt = self._render_sdxl_style_prompt(prompt_blocks, style_transfer_program)
        prompt = self._clean_prompt(prompt)
        prompt = self._limit_words(prompt, 60)
        return prompt, ["compiled SDXL style-only Img2Img prompt"], 60

    def _compile_gpt_image(self, prompt_blocks):
        lines = [
            "Create an image using this structured visual brief.",
            f"Subject: {prompt_blocks.get('subject')}",
            f"Scene: {prompt_blocks.get('scene')}",
            f"Style: {prompt_blocks.get('style')}",
            f"Layout: {prompt_blocks.get('layout')}",
            f"Lighting: {prompt_blocks.get('lighting')}",
            f"Quality: {prompt_blocks.get('quality')}",
        ]
        prompt = self._clean_prompt(" ".join(line for line in lines if line.strip()))
        return prompt, ["compiled GPT Image structured instruction"], 180

    def _negative_prompt(self, context_program, fallback):
        negative = context_program.get("negative") or {}
        return self._join_parts(
            [
                fallback,
                negative.get("negative_prompt", []),
                negative.get("strict_avoid", []),
            ]
        )

    def _character_phrase(self, characters):
        count = characters.get("character_count") or 1
        items = characters.get("characters") or []
        hints = [
            item.get("caption_hint")
            for item in items
            if isinstance(item, dict) and item.get("caption_hint")
        ]
        rules = characters.get("preservation_rules") or []
        return self._join_parts([f"{count} recognizable subject", hints[:3], rules[:2]])

    def _render_prompts(
        self,
        generation_prompt,
        negative_prompt,
        prompt_blocks,
        context_program,
        context_reasoning,
        style_transfer_program,
        provider,
        sanitizer,
        forbidden_concepts,
        provider_rendering=None,
    ):
        provider_rendering = provider_rendering or {}
        sdxl_style_prompt = provider_rendering.get("sdxl_style_prompt") or (
            self._render_sdxl_style_prompt(
                prompt_blocks,
                style_transfer_program,
            )
        )
        generation_budget = 60 if provider in {"sdxl", "sdxl_quality"} else None
        generation_clean = sanitizer.sanitize(
            generation_prompt,
            forbidden_concepts,
            provider=provider,
            max_tokens=generation_budget,
        )
        sdxl_clean = sanitizer.sanitize(
            sdxl_style_prompt,
            forbidden_concepts,
            provider="sdxl",
            max_tokens=60,
        )
        clip_clean = sanitizer.sanitize(
            provider_rendering.get("clip_prompt") or self._render_clip_prompt(prompt_blocks),
            forbidden_concepts,
            provider="clip",
            max_tokens=40,
        )
        pickscore_clean = sanitizer.sanitize(
            provider_rendering.get("pickscore_prompt")
            or self._render_pickscore_prompt(prompt_blocks),
            forbidden_concepts,
            provider="pickscore",
            max_tokens=None,
        )
        vlm_judge_clean = sanitizer.sanitize(
            provider_rendering.get("vlm_judge_prompt")
            or self._render_vlm_judge_prompt(
                prompt_blocks,
                context_program,
                context_reasoning,
            ),
            forbidden_concepts,
            provider="vlm_judge",
            max_tokens=None,
        )
        sanitizer_report = {
            "generation": generation_clean["prompt_sanitizer_report"],
            "sdxl": sdxl_clean["prompt_sanitizer_report"],
            "clip": clip_clean["prompt_sanitizer_report"],
            "pickscore": pickscore_clean["prompt_sanitizer_report"],
            "vlm_judge": vlm_judge_clean["prompt_sanitizer_report"],
        }
        negative_clean = sanitizer.sanitize(
            negative_prompt,
            forbidden_concepts=[],
            provider="negative",
            max_tokens=None,
        )
        return {
            "generation_prompt": generation_clean["prompt"],
            "sdxl_style_prompt": sdxl_clean["prompt"],
            "clip_prompt": clip_clean["prompt"],
            "pickscore_prompt": pickscore_clean["prompt"],
            "vlm_judge_prompt": vlm_judge_clean["prompt"],
            "negative_prompt": negative_clean["prompt"],
            "prompt_sanitizer_report": sanitizer_report,
        }

    def _render_sdxl_style_prompt(self, prompt_blocks, style_transfer_program):
        style = style_transfer_program.get("style") or {}
        layout = style_transfer_program.get("layout") or {}
        parts = [
            style.get("name"),
            style.get("rendering"),
            style.get("mood"),
            style.get("color_palette", []),
            style.get("texture"),
            layout.get("format"),
            layout.get("structure"),
            layout.get("background"),
            layout.get("decorations", []),
            prompt_blocks.get("style"),
            prompt_blocks.get("lighting"),
        ]
        prompt = self._join_parts(parts)
        return self._remove_identity_terms(prompt)

    def _remove_identity_terms(self, prompt):
        identity_terms = (
            "gender",
            "hair",
            "hairstyle",
            "eye color",
            "eyes",
            "outfit",
            "clothing",
            "clothes",
            "accessory",
            "accessories",
            "weapon",
            "sword",
            "female",
            "male",
            "woman",
            "man",
            "girl",
            "boy",
        )
        phrases = []
        for phrase in str(prompt or "").split(","):
            lowered = phrase.lower()
            if any(term in lowered for term in identity_terms):
                continue
            phrases.append(phrase)
        return ", ".join(phrase.strip() for phrase in phrases if phrase.strip())

    def _legacy_render_prompts(
        self,
        generation_prompt,
        negative_prompt,
        prompt_blocks,
        context_program,
        context_reasoning,
    ):
        clip_prompt = self._render_clip_prompt(prompt_blocks)
        pickscore_prompt = self._render_pickscore_prompt(prompt_blocks)
        vlm_judge_prompt = self._render_vlm_judge_prompt(
            prompt_blocks,
            context_program,
            context_reasoning,
        )
        return {
            "generation_prompt": generation_prompt,
            "clip_prompt": clip_prompt,
            "pickscore_prompt": pickscore_prompt,
            "vlm_judge_prompt": vlm_judge_prompt,
            "negative_prompt": negative_prompt,
        }

    def _apply_style_transfer_program(self, prompt_blocks, program):
        style = program.get("style") or {}
        layout = program.get("layout") or {}
        style_bits = [
            style.get("name"),
            style.get("rendering"),
            style.get("mood"),
            style.get("color_palette", []),
            style.get("texture"),
        ]
        layout_bits = [
            layout.get("format"),
            layout.get("structure"),
            layout.get("background"),
            layout.get("decorations", []),
        ]
        prompt_blocks["style"] = self._join_parts(
            [prompt_blocks.get("style"), style_bits]
        )
        prompt_blocks["layout"] = self._join_parts(
            [prompt_blocks.get("layout"), layout_bits]
        )

    def _render_clip_prompt(self, prompt_blocks):
        semantic = self._join_parts(
            [
                prompt_blocks.get("subject"),
                prompt_blocks.get("scene"),
                prompt_blocks.get("layout"),
            ]
        )
        semantic = self._clean_clip_prompt(semantic)
        return self._limit_words(semantic, 40)

    def _render_pickscore_prompt(self, prompt_blocks):
        prompt = self._join_parts(
            [
                prompt_blocks.get("subject"),
                prompt_blocks.get("style"),
                prompt_blocks.get("layout"),
                prompt_blocks.get("lighting"),
                prompt_blocks.get("quality"),
                "appealing composition",
                "coherent style",
                "aesthetic visual balance",
            ]
        )
        return self._clean_prompt(prompt)

    def _render_vlm_judge_prompt(self, prompt_blocks, context_program, context_reasoning):
        criteria = (
            "Compare the reference image and generated image. "
            "Evaluate identity, style, lighting, camera, composition, background, "
            "and prompt alignment. Return an evidence-based visual judgment."
        )
        prompt = self._join_parts(
            [
                criteria,
                f"Subject: {prompt_blocks.get('subject')}",
                f"Scene: {prompt_blocks.get('scene')}",
                f"Style: {prompt_blocks.get('style')}",
                f"Layout: {prompt_blocks.get('layout')}",
                f"Lighting: {prompt_blocks.get('lighting')}",
                f"Quality: {prompt_blocks.get('quality')}",
                f"Reference context: {context_program.get('reference_image') or {}}",
                f"Reasoning context: {context_reasoning}",
            ]
        )
        return self._clean_prompt(prompt)

    def _clean_clip_prompt(self, prompt):
        cleaned = str(prompt or "")
        for term in self.CLIP_REMOVE_TERMS:
            cleaned = cleaned.replace(term, "")
            cleaned = cleaned.replace(term.title(), "")
            cleaned = cleaned.replace(term.upper(), "")
        return self._clean_prompt(cleaned)

    def _join_parts(self, values):
        parts = []
        self._append_value(parts, values)
        parts = [str(part).strip() for part in parts if str(part).strip()]
        return ", ".join(parts)

    def _append_value(self, parts, value):
        if value is None:
            return
        if isinstance(value, str):
            if value.strip():
                parts.append(value)
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                self._append_value(parts, item)
            return
        if isinstance(value, dict):
            for item in value.values():
                self._append_value(parts, item)
            return
        parts.append(value)

    def _clean_prompt(self, prompt):
        cleaned = str(prompt or "").replace("\n", " ")
        for term in self.INTERNAL_TERMS:
            cleaned = cleaned.replace(term, "")
        phrases = []
        seen = set()
        for phrase in cleaned.split(","):
            item = " ".join(phrase.split()).strip(" ,.")
            key = item.lower()
            if item and key not in seen:
                phrases.append(item)
                seen.add(key)
        return ", ".join(phrases)

    def _limit_words(self, prompt, max_words):
        words = str(prompt or "").split()
        if len(words) <= max_words:
            return prompt
        return " ".join(words[:max_words]).rstrip(" ,.")
