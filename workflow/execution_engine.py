from workflow.agent_state import AgentState
from workflow.debug_report import DebugReportManager


class DynamicExecutionEngine:
    DEFAULT_PLAN = [
        "goal_planner",
        "memory_load",
        "vision",
        "character_program_builder",
        "memory_retrieval",
            "retrieval",
            "prompt_compressor",
            "scene_planning",
            "character",
            "style",
            "layout",
            "pose",
            "expression",
            "lighting",
            "negative_prompt",
            "context_program_builder",
            "context_program_validator",
            "prompt_assembler",
            "prompt_critic",
            "llm_prompt_critic",
            "prompt_optimizer",
            "llm_prompt_optimizer",
            "provider_router",
            "prompt_compiler",
            "provider_prompt_adapter",
        "generation",
        "evaluation",
        "reflection",
        "adaptive_planner",
        "retry",
        "memory_save",
    ]

    def run(self, execution_plan: list[str], registry, state: dict) -> dict:
        print("[ExecutionEngine] Starting dynamic execution...")

        agent_state = AgentState.from_dict(state)
        agent_state.validate()
        state = agent_state.to_dict()
        state.setdefault("agent_trace", [])
        planner_goal_tree = (state.get("planner_result") or {}).get("goal_tree")
        if planner_goal_tree and not state.get("goal_tree"):
            state["goal_tree"] = planner_goal_tree
            state["agent_trace"].append("GoalPlanner created goal tree")
        planner_reasoning = (state.get("planner_result") or {}).get("context_reasoning")
        if planner_reasoning and not state.get("context_reasoning"):
            state["context_reasoning"] = planner_reasoning
            state["agent_trace"].append("LLMContextReasoner created semantic plan")
        else:
            self._run_llm_context_reasoner(registry, state)
        plan = self._normalize_plan(execution_plan or self.DEFAULT_PLAN)

        for step in plan:
            print(f"[ExecutionEngine] Running step: {step}")
            try:
                handler = getattr(self, f"_run_{step}", None)
                if handler is None:
                    message = f"Unknown step skipped: {step}"
                    print(f"[ExecutionEngine] {message}")
                    state["agent_trace"].append(message)
                    continue

                handler(registry, state)
                state["agent_trace"].append(f"ExecutionEngine completed {step}")
            except Exception as error:
                message = f"ExecutionEngine error in {step}: {error}"
                print(f"[ExecutionEngine] {message}")
                state["agent_trace"].append(message)
                if step != "memory_save":
                    raise

        print("[ExecutionEngine] Dynamic execution completed.")
        final_state = AgentState.from_dict(state)
        final_state.validate()
        return final_state.to_dict()

    def _run_memory_load(self, registry, state):
        state["last_run"] = registry.call("memory_load")

    def _run_goal_planner(self, registry, state):
        if state.get("goal_tree"):
            print("[ExecutionEngine] Goal tree already available.")
            return
        try:
            self._run_state_step(registry, state, "goal_planner")
            state["agent_trace"].append("GoalPlanner created goal tree")
            print("[ExecutionEngine] GoalPlanner created goal tree")
        except Exception as error:
            print(f"[ExecutionEngine] GoalPlanner failed: {error}")
            state["goal_tree"] = {
                "main_goal": "Generate a coherent high-quality image.",
                "sub_goals": ["preserve subject identity", "maintain clear composition"],
                "priorities": {
                    "identity": 0.8,
                    "style": 0.7,
                    "composition": 0.7,
                    "lighting": 0.6,
                    "background": 0.5,
                },
                "success_criteria": ["generated image matches the user request"],
            }
            state["agent_trace"].append("GoalPlanner used fallback goal tree")

    def _run_llm_context_reasoner(self, registry, state):
        if not hasattr(registry, "has_tool") or not registry.has_tool("llm_context_reasoner"):
            print("[ExecutionEngine] LLMContextReasoner not registered. Skipping.")
            return

        try:
            self._run_state_step(registry, state, "llm_context_reasoner")
            state["agent_trace"].append("LLMContextReasoner created semantic plan")
            print("[ExecutionEngine] LLMContextReasoner created semantic plan")
        except Exception as error:
            print(f"[ExecutionEngine] LLMContextReasoner failed: {error}")
            state["context_reasoning"] = {
                "user_goal": state.get("user_prompt", ""),
                "scene_goal": "semantic planning unavailable",
                "composition_goal": "semantic planning unavailable",
                "interaction_goal": "semantic planning unavailable",
                "style_goal": "semantic planning unavailable",
                "priority": ["character", "emotion", "layout", "style"],
                "mode": "fallback",
            }
            state["agent_trace"].append("LLMContextReasoner skipped after error")

    def _run_vision(self, registry, state):
        state["caption"] = registry.call("vision", state.get("image"))

    def _run_character_program_builder(self, registry, state):
        try:
            self._run_state_step(registry, state, "character_program_builder")
            state["agent_trace"].append("CharacterProgramBuilder created character program")
            print("[ExecutionEngine] CharacterProgramBuilder created character program")
        except Exception as error:
            print(f"[ExecutionEngine] CharacterProgramBuilder failed: {error}")
            state["character_program"] = self._fallback_character_program(state)
            state["agent_trace"].append("CharacterProgramBuilder used fallback program")

    def _run_memory_retrieval(self, registry, state):
        query = f"{state.get('caption', '')} {state.get('user_prompt', '')}".strip()
        try:
            state["memory_context"] = registry.call("memory_retrieval", query)
            print("[ExecutionEngine] Memory context added.")
        except Exception as error:
            print(f"[ExecutionEngine] Memory retrieval failed: {error}")
            state["memory_context"] = {
                "similar_runs": [],
                "best_run": None,
                "memory_hint": "memory unavailable",
                "memory_score": 0.0,
            }

    def _run_retrieval(self, registry, state):
        state["retrieved_context"] = registry.call(
            "retrieval",
            state.get("caption", ""),
            state.get("user_prompt", ""),
        )

    def _run_prompt_compressor(self, registry, state):
        last_run = state.get("last_run")
        prompt_context = {
            "planner_result": state.get("planner_result"),
            "last_run": last_run,
            "retrieved_context": state.get("retrieved_context", {}),
            "memory_context": state.get("memory_context", {}),
            "retry_history": state.get("retry_history", []),
            "style_preferences": state.get("style_preferences"),
            "previous_best_prompt": (
                last_run.get("best_prompt") if isinstance(last_run, dict) else None
            ),
            "previous_best_score": (
                last_run.get("best_score") if isinstance(last_run, dict) else None
            ),
        }
        state["prompt_context"] = prompt_context
        state["compressed_context"] = registry.call(
            "prompt_compressor",
            prompt_context,
        )

    def _run_prompt(self, registry, state):
        final_prompt = registry.call(
            "prompt",
            state.get("caption", ""),
            state.get("user_prompt", ""),
            compressed_context=state.get("compressed_context", {}),
        )
        state["final_prompt"] = self._compress_prompt(
            registry,
            final_prompt,
            max_words=60,
            label="initial",
        )
        state["evaluation_prompt"] = self._make_evaluation_prompt(
            registry,
            state.get("caption", ""),
            state.get("user_prompt", ""),
            state["final_prompt"],
            label="evaluation",
        )

    def _run_prompt_critic(self, registry, state):
        try:
            self._run_state_step(registry, state, "prompt_critic")
            state["agent_trace"].append("PromptCriticAgent generated prompt report")
        except Exception as error:
            print(f"[ExecutionEngine] PromptCritic failed: {error}")
            state["prompt_report"] = None
            state["prompt_quality_score"] = 100
            state["agent_trace"].append("PromptCriticAgent skipped after error")

    def _run_llm_prompt_critic(self, registry, state):
        try:
            self._run_state_step(registry, state, "llm_prompt_critic")
            state["agent_trace"].append("LLMPromptCriticAgent reviewed prompt")
            print("[ExecutionEngine] LLMPromptCriticAgent reviewed prompt")
        except Exception as error:
            print(f"[ExecutionEngine] LLMPromptCritic failed: {error}")
            state["llm_prompt_critic_report"] = {
                "mode": "fallback",
                "critic_score": state.get("prompt_quality_score", 100),
                "semantic_issues": [],
                "conflicts": [],
                "priority_issues": [],
                "provider_suitability_issues": [],
                "suggestions": ["LLM prompt critic failed; kept rule-based critic result"],
                "priority_fix": [],
                "reasoning_summary": str(error),
                "used_fallback": True,
            }
            state["llm_prompt_critic_score"] = state["llm_prompt_critic_report"]["critic_score"]
            state["agent_trace"].append("LLMPromptCriticAgent skipped after error")

    def _run_prompt_optimizer(self, registry, state):
        try:
            self._run_state_step(registry, state, "prompt_optimizer")
            state["agent_trace"].append("PromptOptimizerAgent optimized prompt")
            print("[ExecutionEngine] PromptOptimizerAgent optimized prompt")
            state["evaluation_prompt"] = self._make_evaluation_prompt(
                registry,
                state.get("caption", ""),
                state.get("user_prompt", ""),
                state.get("final_prompt", ""),
                label="evaluation",
            )
        except Exception as error:
            print(f"[ExecutionEngine] PromptOptimizer failed: {error}")
            state["optimization_report"] = {
                "length_before": 0,
                "length_after": 0,
                "duplicates_removed": [],
                "keywords_added": [],
                "keywords_removed": [],
                "actions": ["optimization failed; kept existing prompt"],
            }
            state["agent_trace"].append("PromptOptimizerAgent skipped after error")

    def _run_llm_prompt_optimizer(self, registry, state):
        try:
            self._run_state_step(registry, state, "llm_prompt_optimizer")
            state["agent_trace"].append("LLMPromptOptimizerAgent processed prompt")
            print("[ExecutionEngine] LLMPromptOptimizerAgent processed prompt")
            state["evaluation_prompt"] = self._make_evaluation_prompt(
                registry,
                state.get("caption", ""),
                state.get("user_prompt", ""),
                state.get("final_prompt", ""),
                label="evaluation",
            )
        except Exception as error:
            print(f"[ExecutionEngine] LLMPromptOptimizer failed: {error}")
            prompt = state.get("canonical_prompt") or state.get("final_prompt", "")
            state["llm_optimized_prompt"] = prompt
            state["canonical_prompt"] = prompt
            state["final_prompt"] = prompt
            state["llm_optimizer_report"] = {
                "mode": "disabled",
                "reason": "LLM optimizer failed; kept existing prompt.",
                "changes": [],
                "used_fallback": True,
            }
            state["agent_trace"].append("LLMPromptOptimizerAgent skipped after error")

    def _run_scene_planning(self, registry, state):
        self._run_state_step(registry, state, "scene_planning")
        state["agent_trace"].append("ScenePlanningAgent created scene plan")

    def _run_character(self, registry, state):
        state["character_section"] = registry.call(
            "character",
            state.get("caption", ""),
            state.get("user_prompt", ""),
            context=state,
        )

    def _run_style(self, registry, state):
        state["style_section"] = registry.call(
            "style",
            state.get("user_prompt", ""),
            retrieved_context=state.get("retrieved_context", {}),
        )

    def _run_layout(self, registry, state):
        state["layout_section"] = registry.call(
            "layout",
            state.get("user_prompt", ""),
            planner_result=state.get("planner_result", {}),
            scene_plan=state.get("scene_plan"),
        )

    def _run_pose(self, registry, state):
        state["pose_section"] = registry.call(
            "pose",
            state.get("user_prompt", ""),
            character_section=state.get("character_section", {}),
            scene_plan=state.get("scene_plan"),
        )

    def _run_expression(self, registry, state):
        state["expression_section"] = registry.call(
            "expression",
            state.get("user_prompt", ""),
            scene_plan=state.get("scene_plan"),
        )

    def _run_lighting(self, registry, state):
        state["lighting_section"] = registry.call(
            "lighting",
            state.get("user_prompt", ""),
            retrieved_context=state.get("retrieved_context", {}),
        )

    def _run_negative_prompt(self, registry, state):
        state["negative_section"] = registry.call(
            "negative_prompt",
            state.get("user_prompt", ""),
            retrieved_context=state.get("retrieved_context", {}),
        )

    def _run_context_program_builder(self, registry, state):
        try:
            self._run_state_step(registry, state, "context_program_builder")
            self._apply_goal_tree_context(state)
            self._apply_character_program_context(state)
            state["agent_trace"].append("ContextProgramBuilder created context program")
            print("[ExecutionEngine] ContextProgramBuilder created context program")
        except Exception as error:
            print(f"[ExecutionEngine] ContextProgramBuilder failed: {error}")
            state["context_program"] = {}
            state["context_program_summary"] = "context program unavailable"
            state["context_program_version"] = "v1"
            state["agent_trace"].append("ContextProgramBuilder skipped after error")

    def _run_context_program_validator(self, registry, state):
        try:
            self._run_state_step(registry, state, "context_program_validator")
            state["agent_trace"].append("ContextProgramValidator validated context program")
            print("[ExecutionEngine] ContextProgramValidator validated context program")
        except Exception as error:
            print(f"[ExecutionEngine] ContextProgramValidator failed: {error}")
            state["context_validation"] = {
                "valid": False,
                "missing_keys": [],
                "type_warnings": [str(error)],
                "provider_warnings": [],
                "suggestions": ["validator failed; inspect context_program manually"],
                "score": 0,
            }
            state["agent_trace"].append("ContextProgramValidator skipped after error")

    def _run_prompt_assembler(self, registry, state):
        self._run_state_step(registry, state, "prompt_assembler")
        state["canonical_prompt"] = state.get("canonical_prompt", state.get("final_prompt", ""))
        state["final_prompt"] = self._compress_prompt(
            registry,
            state["canonical_prompt"],
            max_words=120,
            label="generation",
        )
        state.setdefault("negative_prompt", "")
        state.setdefault("prompt_sections", {})
        state["evaluation_prompt"] = self._make_evaluation_prompt(
            registry,
            state.get("caption", ""),
            state.get("user_prompt", ""),
            state["final_prompt"],
            label="evaluation",
        )

    def _run_provider_router(self, registry, state):
        try:
            self._run_state_step(registry, state, "provider_router")
        except Exception as error:
            print(f"[ExecutionEngine] ProviderRouter failed: {error}")
            result = {
                "requested_provider": "flux",
                "selected_provider": "flux",
                "fallback_provider": "flux",
                "reason": "ProviderRouter failed; fallback to flux.",
                "capabilities": {},
            }
            state["provider_routing"] = result
            state["provider"] = result.get("selected_provider", "flux")

        trace = f"ProviderRouter selected provider: {state['provider']}"
        state["agent_trace"].append(trace)
        print(f"[ExecutionEngine] {trace}")

    def _run_prompt_compiler(self, registry, state):
        try:
            self._apply_goal_tree_context(state)
            self._apply_character_program_context(state)
            self._run_state_step(registry, state, "prompt_compiler")
            state["agent_trace"].append("PromptCompiler compiled prompt package")
            print("[ExecutionEngine] PromptCompiler compiled prompt package")
        except Exception as error:
            print(f"[ExecutionEngine] PromptCompiler failed: {error}")
            state["compiled_prompt_package"] = None
            state["agent_trace"].append("PromptCompiler skipped after error")

    def _run_provider_prompt_adapter(self, registry, state):
        try:
            self._run_state_step(registry, state, "provider_prompt_adapter")
        except Exception as error:
            print(f"[ExecutionEngine] Provider prompt adapter failed: {error}")
            canonical_prompt = state.get("canonical_prompt") or state.get("final_prompt", "")
            adapter_result = {
                "provider": "flux",
                "provider_prompt": canonical_prompt,
                "provider_negative_prompt": state.get("negative_prompt") or "",
                "adapter_notes": ["fallback to canonical prompt"],
            }
            state.update(adapter_result)
            state["final_prompt"] = state["provider_prompt"]
        print("[ExecutionEngine] Provider prompt created.")

    def _run_generation(self, registry, state):
        print("[ExecutionEngine] Initial attempt started.")
        self._print_prompt_preview(state)
        state["output_image_path"] = registry.call(
            "generation",
            state.get("final_prompt", ""),
        )

    def _run_evaluation(self, registry, state):
        state["score"] = registry.call(
            "evaluation",
            state.get("image"),
            state.get("output_image_path"),
            state.get("evaluation_prompt", ""),
        )

    def _run_reflection(self, registry, state):
        reflection_result = registry.call(
            "reflection",
            state.get("caption", ""),
            state.get("final_prompt", ""),
            state.get("score", 0.0),
        )
        state["reflection"] = reflection_result.get("reflection")
        raw_suggested_prompt = reflection_result.get(
            "suggested_prompt",
            state.get("final_prompt", ""),
        )
        state["raw_suggested_prompt"] = raw_suggested_prompt
        state["suggested_prompt"] = raw_suggested_prompt
        state["reflection_needs_retry"] = reflection_result.get(
            "needs_retry",
            False,
        )
        state["retry_needed"] = state["reflection_needs_retry"]

    def _run_adaptive_planner(self, registry, state):
        state.setdefault("agent_trace", [])
        try:
            self._run_state_step(registry, state, "adaptive_planner")
            self._apply_adaptive_context_updates(state)
            state["agent_trace"].append("AdaptivePlanner created re-planning strategy")
            print("[ExecutionEngine] AdaptivePlanner created re-planning strategy.")
        except Exception as error:
            print(f"[ExecutionEngine] AdaptivePlanner failed: {error}")
            state["adaptive_plan"] = {
                "failure_analysis": "adaptive planning unavailable",
                "hypothesis": str(error),
                "strategy": "fallback to existing retry prompt",
                "context_updates": [],
                "priority_change": [],
                "confidence": 0.0,
            }
            state["agent_trace"].append("AdaptivePlanner skipped after error")

    def _run_retry(self, registry, state):
        retry_needed = registry.call("retry", state.get("score", 0.0))
        state["retry_needed"] = retry_needed
        state["retry_output_image_path"] = None
        state["retry_score"] = None

        if retry_needed:
            print("[ExecutionEngine] Retry needed. Starting second attempt.")
            self._prepare_adaptive_retry_prompt(registry, state)
            raw_suggested_prompt = state.get("raw_suggested_prompt") or state.get(
                "final_prompt",
                "",
            )
            state["retry_prompt"] = self._compress_prompt(
                registry,
                raw_suggested_prompt,
                max_words=55,
                label="retry",
            )
            state["retry_evaluation_prompt"] = self._make_evaluation_prompt(
                registry,
                state.get("caption", ""),
                state.get("user_prompt", ""),
                state["retry_prompt"],
                label="retry evaluation",
            )
            print("[ExecutionEngine] Using compressed retry prompt.")
            state["retry_output_image_path"] = registry.call(
                "generation",
                state["retry_prompt"],
            )
            state["retry_score"] = registry.call(
                "evaluation",
                state.get("image"),
                state.get("retry_output_image_path"),
                state["retry_evaluation_prompt"],
            )
        else:
            print("[ExecutionEngine] Retry skipped.")
            state["raw_suggested_prompt"] = state.get("raw_suggested_prompt")
            state["retry_prompt"] = None
            state["retry_evaluation_prompt"] = None

        self._select_best_result(state)

    def _run_memory_save(self, registry, state):
        state["memory_saved"] = False
        state["history_path"] = None
        self._save_debug_report(state)

        try:
            state["history_path"] = registry.call(
                "memory_save",
                {
                    "caption": state.get("caption"),
                    "initial_prompt": state.get("final_prompt"),
                    "initial_score": state.get("score"),
                    "initial_output_image_path": state.get("output_image_path"),
                    "evaluation_prompt": state.get("evaluation_prompt"),
                    "negative_prompt": state.get("negative_prompt"),
                    "canonical_prompt": state.get("canonical_prompt"),
                    "provider": state.get("provider"),
                    "provider_prompt": state.get("provider_prompt"),
                    "provider_negative_prompt": state.get("provider_negative_prompt"),
                    "adapter_notes": state.get("adapter_notes"),
                    "reflection": state.get("reflection"),
                    "adaptive_plan": state.get("adaptive_plan"),
                    "retry_needed": state.get("retry_needed"),
                    "retry_prompt": (
                        state.get("retry_prompt")
                        if state.get("retry_needed")
                        else None
                    ),
                    "retry_evaluation_prompt": state.get(
                        "retry_evaluation_prompt"
                    ),
                    "raw_suggested_prompt": state.get("raw_suggested_prompt"),
                    "retry_score": state.get("retry_score"),
                    "retry_output_image_path": state.get("retry_output_image_path"),
                    "best_prompt": state.get("best_prompt"),
                    "best_score": state.get("best_score"),
                    "best_output_image_path": state.get("best_output_image_path"),
                    "debug_report_path": state.get("debug_report_path"),
                    "prompt_preview_path": state.get("prompt_preview_path"),
                    "run_dir": state.get("run_dir"),
                },
            )
            state["memory_saved"] = True
        except Exception as error:
            print(f"[Memory] Save failed: {error}")
            state["agent_trace"].append(f"memory_save failed: {error}")

    def _select_best_result(self, state):
        score = state.get("score")
        retry_score = state.get("retry_score")

        if retry_score is not None and score is not None and retry_score > score:
            state["best_prompt"] = state.get("retry_prompt")
            state["best_output_image_path"] = state.get("retry_output_image_path")
            state["best_score"] = retry_score
        else:
            state["best_prompt"] = state.get("final_prompt")
            state["best_output_image_path"] = state.get("output_image_path")
            state["best_score"] = score

        print(f"[ExecutionEngine] Best score selected: {state.get('best_score')}")

    def _prepare_adaptive_retry_prompt(self, registry, state):
        state.setdefault("agent_trace", [])
        adaptive_plan = state.get("adaptive_plan") or {}
        if not adaptive_plan:
            return

        print("[ExecutionEngine] Applying adaptive re-planning before retry.")
        self._apply_adaptive_context_updates(state)
        try:
            self._run_prompt_compiler(registry, state)
            self._run_provider_prompt_adapter(registry, state)
            compiled_prompt = (
                state.get("provider_prompt")
                or state.get("final_prompt")
                or state.get("raw_suggested_prompt")
            )
            strategy = adaptive_plan.get("strategy")
            if strategy:
                compiled_prompt = f"{compiled_prompt}, adaptive strategy: {strategy}"
            state["raw_suggested_prompt"] = compiled_prompt
            state["agent_trace"].append("AdaptivePlanner updated retry prompt package")
            print("[ExecutionEngine] Adaptive prompt package prepared.")
        except Exception as error:
            print(f"[ExecutionEngine] Adaptive prompt package failed: {error}")
            state["agent_trace"].append(f"adaptive prompt package failed: {error}")

    def _apply_adaptive_context_updates(self, state):
        adaptive_plan = state.get("adaptive_plan") or {}
        context_program = state.get("context_program")
        if not adaptive_plan or not isinstance(context_program, dict):
            return

        updates = adaptive_plan.get("context_updates") or []
        priorities = adaptive_plan.get("priority_change") or []
        if not updates and not priorities:
            return

        characters = context_program.setdefault("characters", {})
        layout = context_program.setdefault("layout", {})
        style = context_program.setdefault("style", {})
        quality = context_program.setdefault("quality", {})

        self._extend_unique(
            characters.setdefault("preservation_rules", []),
            [
                item
                for item in updates
                if "subject" in item or "identity" in item or "caption" in item
            ],
        )
        self._extend_unique(
            layout.setdefault("composition_rules", []),
            [
                item
                for item in updates
                if "layout" in item or "camera" in item or "framing" in item
            ],
        )
        self._extend_unique(
            style.setdefault("rendering_rules", []),
            [item for item in updates if "style" in item],
        )
        self._extend_unique(
            quality.setdefault("quality_keywords", []),
            ["adaptive re-planning", *priorities],
        )
        context_program["adaptive_plan"] = adaptive_plan
        state["context_program"] = context_program

    def _apply_character_program_context(self, state):
        character_program = state.get("character_program") or {}
        context_program = state.get("context_program")
        if not character_program or not isinstance(context_program, dict):
            return

        characters = context_program.setdefault("characters", {})
        character_items = characters.setdefault("characters", [])
        character_hint = self._character_program_hint(character_program)
        if character_hint and not any(
            isinstance(item, dict) and item.get("caption_hint") == character_hint
            for item in character_items
        ):
            character_items.append(
                {
                    "caption_hint": character_hint,
                    "character_program": character_program,
                }
            )

        identity_rules = character_program.get("identity_rules") or []
        self._extend_unique(
            characters.setdefault("preservation_rules", []),
            identity_rules,
        )
        if character_items:
            characters["character_count"] = max(
                characters.get("character_count") or 0,
                len(character_items),
            )
        context_program["character_program"] = character_program
        state["context_program"] = context_program

    def _apply_goal_tree_context(self, state):
        goal_tree = state.get("goal_tree") or {}
        context_program = state.get("context_program")
        if not goal_tree or not isinstance(context_program, dict):
            return

        context_program["goal_tree"] = goal_tree
        priorities = goal_tree.get("priorities") or {}
        success_criteria = goal_tree.get("success_criteria") or []

        quality = context_program.setdefault("quality", {})
        priority_hints = [
            f"{name} priority {score}"
            for name, score in priorities.items()
            if isinstance(score, (int, float)) and score >= 0.8
        ]
        self._extend_unique(
            quality.setdefault("quality_keywords", []),
            priority_hints,
        )
        self._extend_unique(
            quality.setdefault("success_criteria", []),
            success_criteria,
        )

        characters = context_program.setdefault("characters", {})
        if priorities.get("identity", 0) >= 0.9:
            self._extend_unique(
                characters.setdefault("preservation_rules", []),
                ["identity is the highest priority"],
            )

        style = context_program.setdefault("style", {})
        if priorities.get("style", 0) >= 0.9:
            self._extend_unique(
                style.setdefault("rendering_rules", []),
                ["preserve requested style without reducing identity clarity"],
            )

        layout = context_program.setdefault("layout", {})
        if priorities.get("composition", 0) >= 0.8:
            self._extend_unique(
                layout.setdefault("composition_rules", []),
                ["composition priority should remain high"],
            )

        lighting = context_program.setdefault("lighting", {})
        if priorities.get("lighting", 0) >= 0.8:
            self._extend_unique(
                lighting.setdefault("lighting_keywords", []),
                ["priority lighting mood"],
            )
        state["context_program"] = context_program

    def _character_program_hint(self, character_program):
        identity = character_program.get("identity") or {}
        appearance = character_program.get("appearance") or {}
        parts = [
            identity.get("gender"),
            identity.get("role"),
            appearance.get("outfit"),
            ", ".join(appearance.get("accessories") or []),
        ]
        return ", ".join(str(part) for part in parts if part)

    def _fallback_character_program(self, state):
        caption = str(state.get("caption") or "")
        return {
            "identity": {
                "gender": "",
                "estimated_age": "",
                "species": "",
                "role": "",
            },
            "appearance": {
                "hair": "",
                "hair_color": "",
                "eye_color": "",
                "skin": "",
                "outfit": "",
                "accessories": [],
            },
            "style": {
                "anime": "",
                "realism": "",
                "rendering": "",
            },
            "pose": "",
            "expression": "",
            "dominant_colors": [],
            "identity_rules": [
                "preserve recognizable character identity",
                f"stay faithful to caption: {caption}",
            ],
        }

    def _extend_unique(self, target, items):
        seen = {str(item).lower() for item in target}
        for item in items:
            key = str(item).lower()
            if item and key not in seen:
                target.append(item)
                seen.add(key)

    def _compress_prompt(self, registry, prompt, max_words, label):
        compressor = getattr(registry, "_tools", {}).get("prompt_compressor")
        if compressor and hasattr(compressor, "compress_prompt"):
            compressed_prompt = compressor.compress_prompt(
                prompt,
                max_words=max_words,
                label=label,
            )
        else:
            words = str(prompt or "").replace("\n", " ").strip().split()
            compressed_prompt = " ".join(words[:max_words])

        word_count = len(compressed_prompt.split())
        print(f"[ExecutionEngine] {label} prompt word count: {word_count}")
        return compressed_prompt

    def _make_evaluation_prompt(self, registry, caption, user_prompt, prompt, label):
        compressor = getattr(registry, "_tools", {}).get("prompt_compressor")
        if compressor and hasattr(compressor, "make_evaluation_prompt"):
            evaluation_prompt = compressor.make_evaluation_prompt(
                caption,
                user_prompt,
                prompt,
            )
        else:
            fallback = f"{caption or ''} {user_prompt or ''}".strip()
            evaluation_prompt = self._compress_prompt(
                registry,
                fallback,
                max_words=40,
                label=label,
            )

        word_count = len(evaluation_prompt.split())
        print(f"[ExecutionEngine] {label} prompt word count: {word_count}")
        return evaluation_prompt

    def _normalize_plan(self, plan):
        normalized = list(plan)
        if "memory_retrieval" in normalized:
            return normalized

        if "vision" in normalized:
            insert_at = normalized.index("vision") + 1
            normalized.insert(insert_at, "memory_retrieval")
        return normalized

    def _run_state_step(self, registry, state, step):
        print(f"[ExecutionEngine] Running state-based step: {step}")
        result = registry.run_with_state(step, state)
        state.update(result)
        print(f"[ExecutionEngine] State updated by: {step}")
        return result

    def _print_prompt_preview(self, state):
        sections = state.get("prompt_sections") or {}
        print("========== Prompt Preview ==========")
        print(f"Character\n{self._preview_section(sections.get('character'))}")
        print(f"Layout\n{self._preview_section(sections.get('layout'))}")
        print(f"Style\n{self._preview_section(sections.get('style'))}")
        print(f"Lighting\n{self._preview_section(sections.get('lighting'))}")
        print(
            "Negative\n"
            f"{state.get('provider_negative_prompt') or state.get('negative_prompt') or ''}"
        )
        print("====================================")

    def _preview_section(self, section):
        if section is None:
            return ""
        if isinstance(section, dict):
            values = []
            for value in section.values():
                if isinstance(value, list):
                    values.extend(str(item) for item in value[:3])
                elif value:
                    values.append(str(value))
            return ", ".join(values[:5])
        if isinstance(section, list):
            return ", ".join(str(item) for item in section[:5])
        return str(section)

    def _save_debug_report(self, state):
        try:
            manager = DebugReportManager()
            state["run_dir"] = manager.create_run_dir()
            copied_paths = manager.copy_output_images(state)
            state.update(copied_paths)
            state["prompt_preview_path"] = manager.save_prompt_preview(state)
            state["agent_trace"].append("Debug report saved")
            state["debug_report_path"] = manager.save_report(state)
        except Exception as error:
            print(f"[DebugReport] Save failed: {error}")
            state["agent_trace"].append(f"debug_report failed: {error}")
