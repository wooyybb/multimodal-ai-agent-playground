class DynamicExecutionEngine:
    DEFAULT_PLAN = [
        "memory_load",
        "vision",
        "prompt_compressor",
        "prompt",
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
        plan = execution_plan or self.DEFAULT_PLAN

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

    def _run_prompt_compressor(self, registry, state):
        last_run = state.get("last_run")
        prompt_context = {
            "planner_result": state.get("planner_result"),
            "last_run": last_run,
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
        state["final_prompt"] = registry.call(
            "prompt",
            state.get("caption", ""),
            state.get("user_prompt", ""),
            compressed_context=state.get("compressed_context", {}),
        )

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
            state.get("final_prompt", ""),
        )

    def _run_reflection(self, registry, state):
        reflection_result = registry.call(
            "reflection",
            state.get("caption", ""),
            state.get("final_prompt", ""),
            state.get("score", 0.0),
        )
        state["reflection"] = reflection_result.get("reflection")
        state["suggested_prompt"] = reflection_result.get(
            "suggested_prompt",
            state.get("final_prompt", ""),
        )
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
            retry_prompt = state.get("suggested_prompt") or state.get(
                "final_prompt",
                "",
            )
            state["retry_output_image_path"] = registry.call(
                "generation",
                retry_prompt,
            )
            state["retry_score"] = registry.call(
                "evaluation",
                state.get("image"),
                state.get("retry_output_image_path"),
                retry_prompt,
            )
        else:
            print("[ExecutionEngine] Retry skipped.")

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
                    "reflection": state.get("reflection"),
                    "retry_needed": state.get("retry_needed"),
                    "retry_prompt": (
                        state.get("suggested_prompt")
                        if state.get("retry_needed")
                        else None
                    ),
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
            state["best_prompt"] = state.get("suggested_prompt")
            state["best_output_image_path"] = state.get("retry_output_image_path")
            state["best_score"] = retry_score
        else:
            state["best_prompt"] = state.get("final_prompt")
            state["best_output_image_path"] = state.get("output_image_path")
            state["best_score"] = score

        print(f"[ExecutionEngine] Best score selected: {state.get('best_score')}")
