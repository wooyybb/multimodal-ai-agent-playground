class DynamicExecutionEngine:
    DEFAULT_PLAN = [
        "memory_load",
        "vision",
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
            "prompt_assembler",
            "prompt_critic",
            "provider_router",
            "provider_prompt_adapter",
            "generation",
        "evaluation",
        "reflection",
        "retry",
        "memory_save",
    ]

    def run(self, execution_plan: list[str], registry, state: dict) -> dict:
        print("[ExecutionEngine] Starting dynamic execution...")

        state = state or {}
        state.setdefault("agent_trace", [])
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
        return state

    def _run_memory_load(self, registry, state):
        state["last_run"] = registry.call("memory_load")

    def _run_vision(self, registry, state):
        state["caption"] = registry.call("vision", state.get("image"))

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
            prompt_report = registry.call(
                "prompt_critic",
                state.get("canonical_prompt", state.get("final_prompt", "")),
                prompt_sections=state.get("prompt_sections", {}),
                scene_plan=state.get("scene_plan"),
            )
            state["prompt_report"] = prompt_report
            state["prompt_quality_score"] = prompt_report.get("quality_score", 100)
            state["agent_trace"].append("PromptCriticAgent generated prompt report")
        except Exception as error:
            print(f"[ExecutionEngine] PromptCritic failed: {error}")
            state["prompt_report"] = None
            state["prompt_quality_score"] = 100
            state["agent_trace"].append("PromptCriticAgent skipped after error")

    def _run_scene_planning(self, registry, state):
        state["scene_plan"] = registry.call(
            "scene_planning",
            state.get("user_prompt", ""),
            caption=state.get("caption"),
            planner_result=state.get("planner_result"),
        )
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

    def _run_prompt_assembler(self, registry, state):
        assembler_result = registry.call(
            "prompt_assembler",
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
        )
        state["canonical_prompt"] = assembler_result.get(
            "canonical_prompt",
            assembler_result.get("generation_prompt", ""),
        )
        state["final_prompt"] = self._compress_prompt(
            registry,
            state["canonical_prompt"],
            max_words=120,
            label="generation",
        )
        state["negative_prompt"] = assembler_result.get("negative_prompt")
        state["prompt_sections"] = assembler_result.get("prompt_sections", {})
        state["evaluation_prompt"] = self._make_evaluation_prompt(
            registry,
            state.get("caption", ""),
            state.get("user_prompt", ""),
            state["final_prompt"],
            label="evaluation",
        )

    def _run_provider_router(self, registry, state):
        try:
            result = registry.call(
                "provider_router",
                state.get("user_prompt", ""),
                scene_plan=state.get("scene_plan"),
                planner_result=state.get("planner_result"),
                available_providers=["flux"],
            )
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

    def _run_provider_prompt_adapter(self, registry, state):
        canonical_prompt = state.get("canonical_prompt") or state.get("final_prompt", "")
        try:
            adapter_result = registry.call(
                "provider_prompt_adapter",
                canonical_prompt,
                state.get("negative_prompt"),
                provider=state.get("provider", "flux"),
                prompt_sections=state.get("prompt_sections"),
                scene_plan=state.get("scene_plan"),
            )
        except Exception as error:
            print(f"[ExecutionEngine] Provider prompt adapter failed: {error}")
            adapter_result = {
                "provider": "flux",
                "provider_prompt": canonical_prompt,
                "provider_negative_prompt": state.get("negative_prompt") or "",
                "adapter_notes": ["fallback to canonical prompt"],
            }

        state["provider"] = adapter_result.get("provider", "flux")
        state["provider_prompt"] = adapter_result.get("provider_prompt", canonical_prompt)
        state["provider_negative_prompt"] = adapter_result.get(
            "provider_negative_prompt",
            state.get("negative_prompt") or "",
        )
        state["adapter_notes"] = adapter_result.get("adapter_notes", [])
        state["final_prompt"] = state["provider_prompt"]
        print("[ExecutionEngine] Provider prompt created.")

    def _run_generation(self, registry, state):
        print("[ExecutionEngine] Initial attempt started.")
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

    def _run_retry(self, registry, state):
        retry_needed = registry.call("retry", state.get("score", 0.0))
        state["retry_needed"] = retry_needed
        state["retry_output_image_path"] = None
        state["retry_score"] = None

        if retry_needed:
            print("[ExecutionEngine] Retry needed. Starting second attempt.")
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
