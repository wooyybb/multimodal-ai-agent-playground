class ContextProgramBuilder:
    VERSION = "v1"

    def run(self, state: dict) -> dict:
        print("[ContextProgramBuilder] Running...")
        state = state or {}
        context_program = {
            "task": self._task(state),
            "user_goal": self._user_goal(state),
            "scene": self._scene(state),
            "characters": self._characters(state),
            "style": self._style(state),
            "layout": self._layout(state),
            "pose": self._pose(state),
            "expression": self._expression(state),
            "lighting": self._lighting(state),
            "quality": self._quality(state),
            "negative": self._negative(state),
            "memory": self._memory(state),
            "retrieval": self._retrieval(state),
            "provider": self._provider(state),
            "output": self._output(state),
        }
        summary = self._summary(context_program)
        print(f"[ContextProgramBuilder] Context program version: {self.VERSION}")
        print(f"[ContextProgramBuilder] Summary: {summary}")
        return {
            "context_program": context_program,
            "context_program_summary": summary,
            "context_program_version": self.VERSION,
        }

    def _task(self, state):
        planner = state.get("planner_result") or {}
        return {
            "task_type": planner.get("task_type", "image_generation"),
            "intent": planner.get("reason", ""),
            "constraints": {
                "requires_vision": planner.get("requires_vision", False),
                "requires_generation": planner.get("requires_generation", True),
                "requires_evaluation": planner.get("requires_evaluation", True),
                "requires_retry": planner.get("requires_retry", True),
            },
        }

    def _user_goal(self, state):
        prompt = state.get("user_prompt", "")
        return {
            "raw_user_prompt": prompt,
            "interpreted_goal": prompt or "image generation",
        }

    def _scene(self, state):
        scene = state.get("scene_plan") or {}
        return {
            "scene_type": scene.get("scene_type"),
            "emotion": scene.get("emotion"),
            "relationship": scene.get("relationship"),
            "interaction": scene.get("interaction"),
            "narrative": scene.get("narrative"),
            "camera_intent": scene.get("camera_intent"),
        }

    def _characters(self, state):
        section = state.get("character_section") or {}
        return {
            "character_count": section.get("character_count", 0),
            "characters": section.get("characters", []),
            "preservation_rules": section.get("global_character_rules", []),
        }

    def _style(self, state):
        section = state.get("style_section") or {}
        return {
            "style_keywords": section.get("style_keywords", []),
            "rendering_rules": section.get("rendering_rules", []),
        }

    def _layout(self, state):
        section = state.get("layout_section") or {}
        return {
            "layout_type": section.get("layout_type"),
            "aspect_ratio": section.get("aspect_ratio"),
            "frame_structure": section.get("frame_structure"),
            "camera_view": section.get("camera_view"),
            "subject_placement": section.get("subject_placement"),
            "composition_rules": section.get("composition_rules", []),
        }

    def _pose(self, state):
        section = state.get("pose_section") or {}
        return {
            "pose_rules": section.get("pose_rules", []),
            "avoid": section.get("avoid", []),
        }

    def _expression(self, state):
        section = state.get("expression_section") or {}
        return {
            "expression_rules": section.get("expression_rules", []),
            "avoid": section.get("avoid", []),
        }

    def _lighting(self, state):
        section = state.get("lighting_section") or {}
        return {
            "lighting_keywords": section.get("lighting_keywords", []),
            "mood": section.get("mood", section.get("lighting_mood")),
        }

    def _quality(self, state):
        context = state.get("compressed_context") or {}
        retrieved = state.get("retrieved_context") or {}
        return {
            "quality_keywords": retrieved.get("quality_keywords", []),
            "prompt_budget_hint": context.get("quality_hint", "keep prompt compact"),
        }

    def _negative(self, state):
        section = state.get("negative_section") or {}
        return {
            "negative_prompt": section.get("negative_prompt", []),
            "strict_avoid": section.get("strict_avoid", []),
        }

    def _memory(self, state):
        memory = state.get("memory_context") or {}
        best = memory.get("best_run") or {}
        return {
            "memory_hint": memory.get("memory_hint"),
            "similar_run_score": memory.get("memory_score", 0.0),
            "best_run_score": best.get("best_score") or best.get("score"),
        }

    def _retrieval(self, state):
        retrieved = state.get("retrieved_context") or {}
        return {
            "retrieved_style": retrieved.get("style"),
            "retrieved_lighting": retrieved.get("lighting"),
            "retrieved_quality": retrieved.get("quality"),
            "retrieved_negative": retrieved.get("negative"),
        }

    def _provider(self, state):
        routing = state.get("provider_routing") or {}
        return {
            "selected_provider": state.get("provider") or routing.get("selected_provider"),
            "requested_provider": routing.get("requested_provider"),
            "provider_constraints": routing.get("capabilities", {}),
        }

    def _output(self, state):
        layout = state.get("layout_section") or {}
        return {
            "target_format": "image",
            "aspect_ratio": layout.get("aspect_ratio"),
            "save_debug_report": True,
        }

    def _summary(self, context_program):
        scene_type = context_program["scene"].get("scene_type") or "unspecified scene"
        layout_type = context_program["layout"].get("layout_type") or "default layout"
        provider = context_program["provider"].get("selected_provider") or "auto provider"
        return f"{scene_type}, {layout_type}, {provider}"
