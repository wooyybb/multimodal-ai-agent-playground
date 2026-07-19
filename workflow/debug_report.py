import json
import shutil
from datetime import datetime
from pathlib import Path


class DebugReportManager:
    def __init__(self, base_dir="outputs/runs"):
        self.base_dir = Path(base_dir)
        self.run_dir = None
        self.run_id = None
        self.timestamp = None

    def create_run_dir(self) -> str:
        print("[DebugReport] Creating run directory...")
        self.timestamp = datetime.now().isoformat(timespec="seconds")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_id = f"run_{stamp}"
        self.run_dir = self.base_dir / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        return str(self.run_dir)

    def save_report(self, state: dict) -> str:
        print("[DebugReport] Saving report...")
        self._ensure_run_dir()
        report_path = self.run_dir / "report.json"
        report = self._build_report(state)
        with report_path.open("w", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2)
        print(f"[DebugReport] Report saved: {report_path}")
        return str(report_path)

    def save_prompt_preview(self, state: dict) -> str:
        print("[DebugReport] Saving prompt preview...")
        self._ensure_run_dir()
        preview_path = self.run_dir / "prompt_preview.txt"
        preview_path.write_text(self._build_prompt_preview(state), encoding="utf-8")
        return str(preview_path)

    def copy_output_images(self, state: dict) -> dict:
        print("[DebugReport] Copying output images...")
        self._ensure_run_dir()
        copied = {}
        for state_key, filename in (
            ("output_image_path", "initial.png"),
            ("retry_output_image_path", "retry.png"),
            ("best_output_image_path", "best.png"),
        ):
            source = state.get(state_key)
            if not source:
                continue
            source_path = Path(str(source))
            if not source_path.exists() or not source_path.is_file():
                continue
            destination = self.run_dir / filename
            try:
                shutil.copy2(source_path, destination)
                copied[f"debug_{state_key}"] = str(destination)
            except OSError as error:
                print(f"[DebugReport] Image copy skipped: {error}")
        return copied

    def _ensure_run_dir(self):
        if self.run_dir is None:
            self.create_run_dir()

    def _build_report(self, state):
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "agent_architecture_version": self._safe(
                state.get("agent_architecture_version", "v3")
            ),
            "executed_agent_groups": self._safe(
                state.get("executed_agent_groups", [])
            ),
            "component_trace": self._safe(state.get("component_trace", [])),
            "user_prompt": self._safe(state.get("user_prompt")),
            "vision_result": self._safe(self._vision_result(state)),
            "vlm_provider": self._safe(
                (self._vision_result(state) or {}).get("provider")
            ),
            "vlm_used_fallback": self._safe(
                (self._vision_result(state) or {}).get("used_fallback")
            ),
            "vlm_latency": self._safe(
                (self._vision_result(state) or {}).get("latency")
            ),
            "provider": self._safe(state.get("provider")),
            "generation_provider": self._safe(state.get("generation_provider")),
            "generation_mode": self._safe(state.get("generation_mode")),
            "generation_plan": self._safe(state.get("generation_plan")),
            "generation_config": self._safe(state.get("generation_config")),
            "generation_preset": self._safe(state.get("generation_preset")),
            "preset_reason": self._safe(state.get("preset_reason")),
            "environment_overrides": self._safe(state.get("environment_overrides")),
            "generation_prompt_length": self._safe(state.get("prompt_length")),
            "generation_is_mock": self._safe(state.get("generation_is_mock")),
            "fallback_reason": self._safe(state.get("fallback_reason")),
            "generation_error_type": self._safe(state.get("generation_error_type")),
            "generation_error_repr": self._safe(state.get("generation_error_repr")),
            "generation_error_stage": self._safe(state.get("generation_error_stage")),
            "generation_error_traceback": self._safe(
                state.get("generation_error_traceback")
            ),
            "model_id": self._safe(state.get("model_id")),
            "device": self._safe(state.get("device")),
            "dtype": self._safe(state.get("dtype")),
            "cfg": self._safe(state.get("cfg")),
            "strength": self._safe(state.get("strength")),
            "steps": self._safe(state.get("steps")),
            "scheduler": self._safe(state.get("scheduler")),
            "resolution": self._safe(state.get("resolution")),
            "future_hooks": self._safe(state.get("future_hooks")),
            "ip_adapter_status": self._safe(state.get("ip_adapter_status")),
            "ip_adapter_enabled": self._safe(state.get("ip_adapter_enabled")),
            "ip_adapter_loaded": self._safe(state.get("ip_adapter_loaded")),
            "ip_adapter_repo_id": self._safe(state.get("ip_adapter_repo_id")),
            "ip_adapter_subfolder": self._safe(state.get("ip_adapter_subfolder")),
            "ip_adapter_weight_name": self._safe(state.get("ip_adapter_weight_name")),
            "ip_adapter_scale": self._safe(state.get("ip_adapter_scale")),
            "style_program": self._safe(state.get("style_program")),
            "selected_lora": self._safe(state.get("selected_lora")),
            "lora_status": self._safe(state.get("lora_status")),
            "controlnet_status": self._safe(state.get("controlnet_status")),
            "controlnet_enabled": self._safe(
                state.get("controlnet_enabled")
                if state.get("controlnet_enabled") is not None
                else (state.get("controlnet_status") or {}).get("enabled")
            ),
            "controlnet_loaded": self._safe(
                state.get("controlnet_loaded")
                if state.get("controlnet_loaded") is not None
                else (state.get("controlnet_status") or {}).get("loaded")
            ),
            "controlnet_type": self._safe(
                state.get("controlnet_type")
                or (state.get("controlnet_status") or {}).get("type")
            ),
            "controlnet_scale": self._safe(
                state.get("controlnet_scale")
                or (state.get("controlnet_status") or {}).get("scale")
            ),
            "control_image_path": self._safe(
                state.get("control_image_path")
                or (state.get("controlnet_status") or {}).get("control_image_path")
            ),
            "controlnet_fallback_reason": self._safe(
                state.get("controlnet_fallback_reason")
                or (state.get("controlnet_status") or {}).get("fallback_reason")
            ),
            "reference_conditioning_enabled": self._safe(
                state.get("reference_conditioning_enabled")
            ),
            "reference_analysis": self._safe(state.get("reference_analysis")),
            "conditioning_summary": self._safe(state.get("conditioning_summary")),
            "conditioned_reference_path": self._safe(
                state.get("conditioned_reference_path")
            ),
            "conditioning_package": self._safe(state.get("conditioning_package")),
            "conditioning_type": self._safe(state.get("conditioning_type")),
            "used_conditioning_fallback": self._safe(
                state.get("used_conditioning_fallback")
            ),
            "conditioning_fallback_reason": self._safe(
                state.get("conditioning_fallback_reason")
            ),
            "conditioning_reason": self._safe(state.get("conditioning_reason")),
            "context_cache": self._safe(state.get("context_cache")),
            "context_cache_path": self._safe(state.get("context_cache_path")),
            "executed_layers": self._safe(state.get("executed_layers", [])),
            "skipped_layers": self._safe(state.get("skipped_layers", [])),
            "dirty_reasons": self._safe(state.get("dirty_reasons", [])),
            "planning_mode": self._safe(state.get("planning_mode")),
            "llm_tool_planner_enabled": self._safe(
                state.get("llm_tool_planner_enabled")
            ),
            "tool_plan": self._safe(state.get("tool_plan")),
            "plan_validation_result": self._safe(
                state.get("plan_validation_result")
            ),
            "selected_tools": self._safe(state.get("selected_tools", [])),
            "executed_tools": self._safe(state.get("executed_tools", [])),
            "skipped_tools": self._safe(state.get("skipped_tools", [])),
            "tool_arguments": self._safe(state.get("tool_arguments", {})),
            "tool_results_summary": self._safe(
                state.get("tool_results_summary", {})
            ),
            "planner_used_fallback": self._safe(
                state.get("planner_used_fallback")
            ),
            "planner_fallback_reason": self._safe(
                state.get("planner_fallback_reason")
            ),
            "replan_count": self._safe(state.get("replan_count", 0)),
            "replan_reason": self._safe(state.get("replan_reason", "")),
            "final_stop_condition": self._safe(
                state.get("final_stop_condition", "")
            ),
            "llm_provider": self._safe(self._llm_summary(state).get("llm_provider")),
            "llm_used_fallback": self._safe(
                self._llm_summary(state).get("llm_used_fallback")
            ),
            "llm_reasoning_raw_text": self._safe(
                self._llm_summary(state).get("llm_reasoning_raw_text")
            ),
            "llm_requirement_parser_enabled": self._safe(
                self._requirement_parser_summary(state).get("enabled")
            ),
            "parser_provider": self._safe(
                self._requirement_parser_summary(state).get("provider")
            ),
            "parser_used_fallback": self._safe(
                self._requirement_parser_summary(state).get("used_fallback")
            ),
            "parser_error": self._safe(
                self._requirement_parser_summary(state).get("error")
            ),
            "llm_raw_text": self._safe(
                self._requirement_parser_summary(state).get("raw_text")
            ),
            "requirement_reasoning_summary": self._safe(
                self._requirement_parser_summary(state).get("reasoning_summary")
            ),
            "planner_result": self._safe(state.get("planner_result")),
            "goal_tree": self._safe(state.get("goal_tree")),
            "context_reasoning": self._safe(state.get("context_reasoning")),
            "scene_plan": self._safe(state.get("scene_plan")),
            "memory_context": self._safe(state.get("memory_context")),
            "retrieved_context": self._safe(state.get("retrieved_context")),
            "context_program": self._safe(state.get("context_program")),
            "context_program_summary": self._safe(state.get("context_program_summary")),
            "context_program_version": self._safe(state.get("context_program_version")),
            "context_validation": self._safe(state.get("context_validation")),
            "reference_image": self._safe(state.get("reference_image")),
            "character_program": self._safe(state.get("character_program")),
            "character_section": self._safe(state.get("character_section")),
            "style_section": self._safe(state.get("style_section")),
            "layout_section": self._safe(state.get("layout_section")),
            "pose_section": self._safe(state.get("pose_section")),
            "expression_section": self._safe(state.get("expression_section")),
            "lighting_section": self._safe(state.get("lighting_section")),
            "negative_section": self._safe(state.get("negative_section")),
            "canonical_prompt": self._safe(state.get("canonical_prompt")),
            "prompt_report": self._safe(state.get("prompt_report")),
            "prompt_quality_score": self._safe(state.get("prompt_quality_score")),
            "llm_prompt_critic_report": self._safe(state.get("llm_prompt_critic_report")),
            "llm_prompt_critic_score": self._safe(state.get("llm_prompt_critic_score")),
            "optimization_report": self._safe(state.get("optimization_report")),
            "llm_optimizer_report": self._safe(state.get("llm_optimizer_report")),
            "provider_prompt": self._safe(state.get("provider_prompt")),
            "compiled_prompt_package": self._safe(state.get("compiled_prompt_package")),
            "reference_conditioning_package": self._safe(
                state.get("reference_conditioning_package")
                or (state.get("compiled_prompt_package") or {}).get(
                    "reference_conditioning_package"
                )
            ),
            "prompt_rendering": self._safe(state.get("prompt_rendering")),
            "provider_prompt_rendering": self._safe(
                state.get("provider_prompt_rendering")
            ),
            "provider_prompt_type": self._safe(state.get("provider_prompt_type")),
            "dense_generation_prompt": self._safe(state.get("dense_generation_prompt")),
            "generation_prompt": self._safe(state.get("generation_prompt")),
            "style_prompt": self._safe(state.get("style_prompt")),
            "style_prompt_word_count": self._safe(
                state.get("style_prompt_word_count")
            ),
            "style_prompt_token_count": self._safe(
                state.get("style_prompt_token_count")
            ),
            "style_transfer_program": self._safe(state.get("style_transfer_program")),
            "llm_style_transfer_program": self._safe(
                state.get("llm_style_transfer_program")
            ),
            "llm_style_transfer_metadata": self._safe(
                state.get("llm_style_transfer_metadata")
            ),
            "llm_reasoning_summary": self._safe(state.get("llm_reasoning_summary")),
            "final_style_transfer_program": self._safe(
                state.get("final_style_transfer_program")
            ),
            "generation_strategy": self._safe(state.get("generation_strategy")),
            "semantic_prompt_program": self._safe(state.get("semantic_prompt_program")),
            "semantic_merge_report": self._safe(state.get("semantic_merge_report")),
            "conflict_resolution_report": self._safe(
                state.get("conflict_resolution_report")
            ),
            "provider_render_report": self._safe(state.get("provider_render_report")),
            "provider_prompt_compiler_report": self._safe(
                (state.get("prompt_rendering") or {}).get(
                    "provider_prompt_compiler_report"
                )
                or state.get("provider_prompt_compiler_report")
                or state.get("provider_render_report")
            ),
            "forbidden_concepts": self._safe(state.get("forbidden_concepts")),
            "prompt_sanitizer_report": self._safe(
                state.get("prompt_sanitizer_report")
            ),
            "prompt_validation_report": self._safe(
                state.get("prompt_validation_report")
            ),
            "sdxl_style_prompt": self._safe(state.get("sdxl_style_prompt")),
            "clip_prompt": self._safe(state.get("clip_prompt")),
            "pickscore_prompt": self._safe(state.get("pickscore_prompt")),
            "vlm_judge_prompt": self._safe(state.get("vlm_judge_prompt")),
            "metric_prompts": self._safe(state.get("metric_prompts")),
            "provider_negative_prompt": self._safe(state.get("provider_negative_prompt")),
            "evaluation_prompt": self._safe(state.get("evaluation_prompt")),
            "evaluation_result": self._safe(self._evaluation_result(state)),
            "metric_routing_info": self._safe(
                (self._evaluation_result(state) or {}).get("metric_routing")
            ),
            "dino_identity_metric": self._safe(self._metric_result(state, "dino_identity")),
            "metrics": self._safe((self._evaluation_result(state) or {}).get("metrics")),
            "weighted_score": self._safe(
                (self._evaluation_result(state) or {}).get("weighted_score")
            ),
            "metric_summary": self._safe(
                (self._evaluation_result(state) or {}).get("metric_summary")
            ),
            "initial_output_image_path": self._safe(state.get("output_image_path")),
            "initial_score": self._safe(state.get("score")),
            "self_verification": self._safe(state.get("self_verification")),
            "hypothesis": self._safe(state.get("hypothesis")),
            "hypothesis_evidence": self._safe(state.get("hypothesis_evidence")),
            "hypothesis_reasoning": self._safe(state.get("hypothesis_reasoning")),
            "candidate_strategies": self._safe(state.get("candidate_strategies")),
            "selected_strategy": self._safe(state.get("selected_strategy")),
            "strategy_reasoning": self._safe(state.get("strategy_reasoning")),
            "adaptive_plan": self._safe(state.get("adaptive_plan")),
            "retry_needed": self._safe(state.get("retry_needed")),
            "raw_suggested_prompt": self._safe(state.get("raw_suggested_prompt")),
            "retry_prompt": self._safe(state.get("retry_prompt")),
            "retry_evaluation_prompt": self._safe(state.get("retry_evaluation_prompt")),
            "retry_output_image_path": self._safe(state.get("retry_output_image_path")),
            "retry_score": self._safe(state.get("retry_score")),
            "best_output_image_path": self._safe(state.get("best_output_image_path")),
            "best_score": self._safe(state.get("best_score")),
            "run_dir": self._safe(state.get("run_dir")),
            "prompt_preview_path": self._safe(state.get("prompt_preview_path")),
            "agent_trace": self._safe(state.get("agent_trace", [])),
        }

    def _build_prompt_preview(self, state):
        lines = []
        self._append_block(lines, "USER REQUEST", state.get("user_prompt"))
        self._append_block(
            lines,
            "AGENT ARCHITECTURE",
            {
                "version": state.get("agent_architecture_version", "v3"),
                "executed_agent_groups": state.get("executed_agent_groups", []),
                "component_trace": state.get("component_trace", []),
            },
        )
        self._append_block(
            lines,
            "INCREMENTAL EXECUTION",
            {
                "context_cache": state.get("context_cache"),
                "context_cache_path": state.get("context_cache_path"),
                "executed_layers": state.get("executed_layers", []),
                "skipped_layers": state.get("skipped_layers", []),
                "dirty_reasons": state.get("dirty_reasons", []),
                "executed_tools": state.get("executed_tools", []),
                "skipped_tools": state.get("skipped_tools", []),
            },
        )
        self._append_block(lines, "DYNAMIC TOOL PLAN", self._dynamic_tool_plan_preview(state))
        self._append_block(lines, "PLAN VALIDATION", self._plan_validation_preview(state))
        self._append_block(lines, "REPLANNING", self._replanning_preview(state))
        self._append_block(lines, "GOAL TREE", state.get("goal_tree"))
        self._append_block(
            lines,
            "VISION RESULT",
            self._vision_result_preview(self._vision_result(state)),
        )
        self._append_block(
            lines,
            "VLM SUMMARY",
            self._vlm_summary(self._vision_result(state)),
        )
        self._append_block(lines, "CONTEXT REASONING", state.get("context_reasoning"))
        self._append_block(lines, "SCENE PLAN", state.get("scene_plan"))
        self._append_block(
            lines,
            "REFERENCE IMAGE",
            self._reference_image_preview(state.get("reference_image")),
        )
        self._append_block(
            lines,
            "CONTEXT PROGRAM",
            {
                "version": state.get("context_program_version"),
                "summary": state.get("context_program_summary"),
                "validation": state.get("context_validation"),
                "program": state.get("context_program"),
            },
        )
        self._append_block(
            lines,
            "CHARACTER PROGRAM",
            self._character_program_preview(state.get("character_program")),
        )
        self._append_block(lines, "CHARACTER", state.get("character_section"))
        self._append_block(lines, "STYLE", state.get("style_section"))
        self._append_block(lines, "LAYOUT", state.get("layout_section"))
        self._append_block(
            lines,
            "POSE / EXPRESSION",
            {
                "pose": state.get("pose_section"),
                "expression": state.get("expression_section"),
            },
        )
        self._append_block(lines, "CANONICAL PROMPT", state.get("canonical_prompt"))
        self._append_block(lines, "PROMPT CRITIC", state.get("prompt_report"))
        self._append_block(
            lines,
            "LLM PROMPT CRITIC",
            self._llm_prompt_critic_preview(state.get("llm_prompt_critic_report")),
        )
        self._append_block(lines, "OPTIMIZED PROMPT", state.get("optimized_prompt"))
        self._append_block(
            lines,
            "SELF VERIFICATION",
            self._self_verification_preview(state.get("self_verification")),
        )
        self._append_block(
            lines,
            "STRATEGY",
            self._strategy_preview(
                state.get("candidate_strategies"),
                state.get("selected_strategy"),
                state.get("strategy_reasoning"),
            ),
        )
        self._append_block(
            lines,
            "ADAPTIVE PLAN",
            self._adaptive_plan_preview(state.get("adaptive_plan")),
        )
        self._append_block(
            lines,
            "COMPILED PROMPT PACKAGE",
            self._compiled_prompt_package_preview(state.get("compiled_prompt_package")),
        )
        self._append_block(
            lines,
            "PROMPT RENDERING",
            self._prompt_rendering_preview(state),
        )
        self._append_block(
            lines,
            "STYLE TRANSFER PROGRAM",
            state.get("style_transfer_program"),
        )
        self._append_block(
            lines,
            "LLM REQUIREMENT PARSER",
            self._requirement_parser_preview(state),
        )
        self._append_block(
            lines,
            "REQUIREMENT STYLE TRANSFER PROGRAM",
            self._requirement_style_transfer_program(state),
        )
        self._append_block(
            lines,
            "LLM STYLE TRANSFER PLANNER",
            self._llm_style_transfer_preview(state),
        )
        self._append_semantic_prompt_sections(lines, state.get("semantic_prompt_program"))
        self._append_block(
            lines,
            "SEMANTIC MERGE",
            state.get("semantic_merge_report"),
        )
        self._append_block(
            lines,
            "CONFLICT RESOLUTION",
            state.get("conflict_resolution_report"),
        )
        self._append_block(
            lines,
            "PROVIDER RENDERER",
            state.get("provider_render_report"),
        )
        self._append_block(
            lines,
            "PROVIDER PROMPT COMPILER V2",
            self._provider_prompt_compiler_preview(state),
        )
        self._append_block(lines, "SDXL PROMPT", state.get("sdxl_style_prompt"))
        self._append_block(
            lines,
            "FLUX PROMPT",
            (state.get("prompt_rendering") or {}).get("flux_prompt")
            or state.get("dense_generation_prompt")
            or state.get("generation_prompt"),
        )
        self._append_block(lines, "CLIP PROMPT", state.get("clip_prompt"))
        self._append_block(
            lines,
            "NEGATIVE PROMPT",
            state.get("provider_negative_prompt") or state.get("negative_prompt"),
        )
        self._append_block(lines, "FORBIDDEN CONCEPTS", state.get("forbidden_concepts"))
        self._append_block(
            lines,
            "PROMPT SANITIZER",
            state.get("prompt_sanitizer_report"),
        )
        self._append_block(
            lines,
            "PROMPT VALIDATION",
            state.get("prompt_validation_report"),
        )
        self._append_block(
            lines,
            "REFERENCE CONDITIONING",
            self._reference_conditioning_preview(state),
        )
        self._append_block(
            lines,
            "REFERENCE CONDITIONING PIPELINE",
            self._reference_conditioning_pipeline_preview(state),
        )
        self._append_block(
            lines,
            "IP-ADAPTER",
            self._ip_adapter_preview(state),
        )
        self._append_block(
            lines,
            "CONTROLNET",
            self._controlnet_preview(state),
        )
        self._append_block(lines, "PROVIDER PROMPT", state.get("provider_prompt"))
        self._append_block(
            lines,
            "GENERATION ROUTING",
            self._generation_routing_preview(state),
        )
        self._append_block(
            lines,
            "GENERATION PRESET",
            self._generation_preset_preview(state),
        )
        self._append_block(
            lines,
            "STYLE TRANSFER",
            self._style_transfer_preview(state),
        )
        self._append_block(
            lines,
            "EVALUATION PROMPT ROUTING",
            self._evaluation_prompt_routing_preview(state),
        )
        self._append_block(
            lines,
            "EVALUATION RESULT",
            self._evaluation_preview(state),
        )
        self._append_block(
            lines,
            "DINO IDENTITY METRIC",
            self._dino_metric_preview(state),
        )
        self._append_block(lines, "AGENT TRACE", "\n".join(state.get("agent_trace", [])))
        return "\n".join(lines).strip() + "\n"

    def _dynamic_tool_plan_preview(self, state):
        plan = state.get("tool_plan") or {}
        steps = []
        for step in plan.get("steps") or []:
            if not isinstance(step, dict):
                continue
            steps.append(
                f"{step.get('step_id')}. {step.get('tool')} / {step.get('reason')}"
            )
        return {
            "Goal": plan.get("goal"),
            "Strategy": plan.get("selected_strategy"),
            "Confidence": plan.get("confidence"),
            "Planning Mode": state.get("planning_mode"),
            "LLM Tool Planner Enabled": state.get("llm_tool_planner_enabled"),
            "Planner Fallback": state.get("planner_used_fallback"),
            "Selected Tools": state.get("selected_tools", []),
            "Steps": steps,
        }

    def _plan_validation_preview(self, state):
        result = state.get("plan_validation_result") or {}
        return {
            "Valid": result.get("valid"),
            "Warnings": result.get("warnings", []),
            "Errors": result.get("errors", []),
            "Fallback": result.get("fallback_used"),
            "Execution Plan": result.get("execution_plan", []),
        }

    def _replanning_preview(self, state):
        return {
            "Count": state.get("replan_count", 0),
            "Reason": state.get("replan_reason", ""),
            "Changed Tools": state.get("replan_changed_tools", []),
            "Changed Parameters": state.get("replan_changed_parameters", {}),
            "Final Stop Condition": state.get("final_stop_condition", ""),
        }
    def _append_block(self, lines, title, value):
        lines.append(f"========== {title} ==========")
        lines.append(self._to_text(value))
        lines.append("")

    def _append_semantic_prompt_sections(self, lines, program):
        program = program or {}
        for title, key in (
            ("Identity", "identity"),
            ("Style", "style"),
            ("Layout", "layout"),
            ("Scene", "scene"),
            ("Lighting", "lighting"),
            ("Quality", "quality"),
            ("Negative", "negative"),
            ("Constraints", "constraints"),
        ):
            self._append_block(lines, title, program.get(key))

    def _provider_prompt_compiler_preview(self, state):
        rendering = state.get("prompt_rendering") or {}
        report = (
            rendering.get("provider_prompt_compiler_report")
            or state.get("provider_prompt_compiler_report")
            or state.get("provider_render_report")
            or {}
        )
        return {
            "Provider": report.get("provider") or state.get("provider"),
            "Prompt Type": report.get("prompt_type")
            or state.get("provider_prompt_type"),
            "Token Count": report.get("token_count"),
            "Removed Low Priority Phrases": report.get(
                "removed_low_priority_phrases", []
            ),
            "Removed Internal Control Tokens": report.get(
                "removed_internal_control_tokens", []
            ),
        }

    def _to_text(self, value):
        safe_value = self._safe(value)
        if isinstance(safe_value, (dict, list)):
            return json.dumps(safe_value, ensure_ascii=False, indent=2)
        if safe_value is None:
            return ""
        return str(safe_value)

    def _llm_prompt_critic_preview(self, report):
        report = report or {}
        return {
            "mode": report.get("mode"),
            "score": report.get("critic_score"),
            "semantic issues": report.get("semantic_issues", []),
            "conflicts": report.get("conflicts", []),
            "priority issues": report.get("priority_issues", []),
            "provider suitability": report.get("provider_suitability_issues", []),
            "suggestions": report.get("suggestions", []),
            "summary": report.get("reasoning_summary"),
        }

    def _llm_style_transfer_preview(self, state):
        program = state.get("llm_style_transfer_program") or {}
        return {
            "task_type": program.get("task_type"),
            "style_goal": program.get("style_goal"),
            "identity_policy": program.get("identity_policy", {}),
            "style": program.get("style", {}),
            "layout": program.get("layout", {}),
            "generation_strategy": program.get("generation_strategy", {}),
            "forbidden_concepts": program.get("forbidden_concepts", []),
            "reasoning_summary": state.get("llm_reasoning_summary")
            or program.get("reasoning_summary"),
            "used_fallback": state.get("llm_used_fallback"),
            "metadata": state.get("llm_style_transfer_metadata", {}),
            "final_style_transfer_program": state.get("final_style_transfer_program"),
        }

    def _requirement_parser_summary(self, state):
        planner = state.get("planner_result") or {}
        summary = planner.get("requirement_parser") or {}
        if not summary:
            program = state.get("style_transfer_program") or {}
            summary = program.get("requirement_parser") or {}
        return {
            "enabled": summary.get("enabled", False),
            "provider": summary.get("provider")
            or planner.get("parser_provider")
            or "rule",
            "used_fallback": summary.get(
                "used_fallback",
                planner.get("parser_used_fallback", True),
            ),
            "error": summary.get("error") or planner.get("parser_error", ""),
            "raw_text": summary.get("raw_text") or planner.get("llm_raw_text", ""),
            "reasoning_summary": summary.get("reasoning_summary")
            or planner.get("reasoning_summary", ""),
        }

    def _requirement_style_transfer_program(self, state):
        planner = state.get("planner_result") or {}
        return planner.get("style_transfer_program") or state.get("style_transfer_program")

    def _requirement_parser_preview(self, state):
        summary = self._requirement_parser_summary(state)
        return {
            "provider": summary.get("provider"),
            "fallback": summary.get("used_fallback"),
            "error": summary.get("error"),
            "reasoning_summary": summary.get("reasoning_summary"),
        }

    def _compiled_prompt_package_preview(self, package):
        package = package or {}
        return {
            "provider": package.get("provider"),
            "positive_prompt": package.get("positive_prompt"),
            "negative_prompt": package.get("negative_prompt"),
            "prompt_rendering": package.get("prompt_rendering", {}),
            "prompt_blocks": package.get("prompt_blocks", {}),
            "compiler_notes": package.get("compiler_notes", []),
        }

    def _prompt_rendering_preview(self, state):
        rendering = state.get("prompt_rendering") or {}
        return {
            "generation_prompt": state.get("generation_prompt")
            or rendering.get("generation_prompt"),
            "provider_prompt_type": state.get("provider_prompt_type"),
            "provider_prompt_rendering": state.get("provider_prompt_rendering"),
            "dense_generation_prompt": state.get("dense_generation_prompt"),
            "sdxl_style_prompt": state.get("sdxl_style_prompt")
            or rendering.get("sdxl_style_prompt"),
            "style_prompt": state.get("style_prompt"),
            "style_prompt_word_count": state.get("style_prompt_word_count"),
            "style_prompt_token_count": state.get("style_prompt_token_count"),
            "clip_prompt": state.get("clip_prompt") or rendering.get("clip_prompt"),
            "pickscore_prompt": state.get("pickscore_prompt")
            or rendering.get("pickscore_prompt"),
            "vlm_judge_prompt": state.get("vlm_judge_prompt")
            or rendering.get("vlm_judge_prompt"),
            "metric_prompts": state.get("metric_prompts"),
            "negative_prompt": state.get("negative_prompt")
            or rendering.get("negative_prompt"),
            "provider_render_report": state.get("provider_render_report"),
        }

    def _reference_conditioning_preview(self, state):
        package = state.get("reference_conditioning_package") or (
            state.get("compiled_prompt_package") or {}
        ).get("reference_conditioning_package") or {}
        return {
            "enabled": package.get("enabled"),
            "type": package.get("conditioning_type"),
            "reference_image_path": package.get("reference_image_path"),
            "identity_strength": package.get("identity_strength"),
            "style_strength": package.get("style_strength"),
            "structure_strength": package.get("structure_strength"),
            "ip_adapter_enabled": (
                state.get("ip_adapter_status") or {}
            ).get("enabled"),
            "ip_adapter_loaded": (
                state.get("ip_adapter_status") or {}
            ).get("loaded"),
            "ip_adapter_repo_id": (
                state.get("ip_adapter_status") or {}
            ).get("repo_id"),
            "ip_adapter_subfolder": (
                state.get("ip_adapter_status") or {}
            ).get("subfolder"),
            "ip_adapter_weight_name": (
                state.get("ip_adapter_status") or {}
            ).get("weight_name"),
            "ip_adapter_scale": (
                state.get("ip_adapter_status") or {}
            ).get("scale"),
            "fallback": state.get("used_conditioning_fallback"),
            "fallback_reason": state.get("conditioning_fallback_reason"),
            "reason": state.get("conditioning_reason")
            or (state.get("ip_adapter_status") or {}).get("reason"),
            "preserve": package.get("preserve", {}),
            "notes": package.get("notes", []),
        }

    def _reference_conditioning_pipeline_preview(self, state):
        return {
            "reference_analysis": state.get("reference_analysis"),
            "conditioning_summary": state.get("conditioning_summary"),
            "conditioned_reference_path": state.get("conditioned_reference_path"),
            "conditioning_package": state.get("conditioning_package"),
        }

    def _ip_adapter_preview(self, state):
        status = state.get("ip_adapter_status") or {}
        return {
            "enabled": state.get("ip_adapter_enabled", status.get("enabled")),
            "loaded": state.get("ip_adapter_loaded", status.get("loaded")),
            "repo_id": state.get("ip_adapter_repo_id", status.get("repo_id")),
            "subfolder": state.get("ip_adapter_subfolder", status.get("subfolder")),
            "weight_name": state.get(
                "ip_adapter_weight_name",
                status.get("weight_name"),
            ),
            "scale": state.get("ip_adapter_scale", status.get("scale")),
            "fallback": state.get(
                "used_conditioning_fallback",
                status.get("used_fallback"),
            ),
            "reason": state.get("conditioning_fallback_reason")
            or status.get("fallback_reason")
            or status.get("reason"),
        }

    def _controlnet_preview(self, state):
        status = state.get("controlnet_status") or {}
        return {
            "enabled": state.get("controlnet_enabled", status.get("enabled")),
            "loaded": state.get("controlnet_loaded", status.get("loaded")),
            "type": state.get("controlnet_type", status.get("type")),
            "scale": state.get("controlnet_scale", status.get("scale")),
            "control_image_path": state.get(
                "control_image_path",
                status.get("control_image_path"),
            ),
            "fallback_reason": state.get(
                "controlnet_fallback_reason",
                status.get("fallback_reason"),
            ),
        }

    def _adaptive_plan_preview(self, plan):
        plan = plan or {}
        return {
            "Failure Analysis": plan.get("failure_analysis"),
            "Hypothesis": plan.get("hypothesis"),
            "Strategy": plan.get("strategy"),
            "Context Updates": plan.get("context_updates", []),
            "Priority Change": plan.get("priority_change", []),
            "Confidence": plan.get("confidence"),
        }

    def _strategy_preview(self, candidates, selected, reasoning=None):
        selected = selected or {}
        return {
            "Candidates": candidates or [],
            "Selected": selected,
            "Reason": selected.get("reason"),
            "Expected Effect": selected.get("expected_effect"),
            "Reasoning": reasoning or {},
        }

    def _self_verification_preview(self, verification):
        verification = verification or {}
        return {
            "overall_pass": verification.get("overall_pass"),
            "goal_satisfaction_score": verification.get("goal_satisfaction_score"),
            "prompt_consistency_score": verification.get("prompt_consistency_score"),
            "context_consistency_score": verification.get("context_consistency_score"),
            "needs_replanning": verification.get("needs_replanning"),
            "findings": verification.get("verification_findings", []),
            "blocking issues": verification.get("blocking_issues", []),
            "recommendations": verification.get("recommendations", []),
        }

    def _character_program_preview(self, program):
        program = program or {}
        return {
            "Identity": program.get("identity", {}),
            "Appearance": program.get("appearance", {}),
            "Style": program.get("style", {}),
            "Pose": program.get("pose"),
            "Expression": program.get("expression"),
            "Dominant Colors": program.get("dominant_colors", []),
            "Identity Rules": program.get("identity_rules", []),
        }

    def _reference_image_preview(self, reference_image):
        reference_image = reference_image or {}
        return {
            "Identity": reference_image.get("identity", {}),
            "Appearance": reference_image.get("appearance", {}),
            "Style": reference_image.get("style", {}),
            "Composition": reference_image.get("composition", {}),
            "Colors": reference_image.get("colors", {}),
            "Identity Rules": reference_image.get("identity_rules", []),
        }

    def _vision_result(self, state):
        vision_result = state.get("vision_result")
        if vision_result:
            return vision_result
        caption = state.get("caption")
        return getattr(caption, "vision_result", None)

    def _evaluation_result(self, state):
        evaluation_result = state.get("evaluation_result")
        if evaluation_result:
            return evaluation_result
        score = state.get("score")
        return getattr(score, "evaluation_result", None)

    def _metric_result(self, state, name):
        result = self._evaluation_result(state) or {}
        for item in result.get("metrics") or []:
            if isinstance(item, dict) and item.get("name") == name:
                return item
        return {}

    def _evaluation_preview(self, state):
        result = self._evaluation_result(state) or {}
        metrics = result.get("metrics") or []
        metric_map = {item.get("name"): item for item in metrics if isinstance(item, dict)}
        return {
            "semantic_alignment": result.get("semantic_alignment"),
            "identity_preservation": result.get("identity_preservation"),
            "prompt_consistency": result.get("prompt_consistency"),
            "aesthetic_quality": result.get("aesthetic_quality"),
            "overall_score": result.get("overall_score"),
            "weighted_score": result.get("weighted_score", state.get("score")),
            "metric_summary": result.get("metric_summary"),
            "used_fallback": result.get("used_fallback"),
            "Metrics": [
                {
                    "name": item.get("name"),
                    "score": item.get("score"),
                    "enabled": item.get("enabled"),
                    "reason": item.get("reason"),
                }
                for item in metrics
                if isinstance(item, dict)
            ],
            "CLIP": metric_map.get("clip", {}),
            "Identity": metric_map.get("identity", {}),
            "Prompt": metric_map.get("prompt", {}),
            "Aesthetic": metric_map.get("aesthetic", {}),
            "VLM Judge": metric_map.get("vlm_judge", {}),
            "DINO Identity": metric_map.get("dino_identity", {}),
            "retry": state.get("retry_needed"),
            "best_score": state.get("best_score"),
        }

    def _evaluation_prompt_routing_preview(self, state):
        result = self._evaluation_result(state) or {}
        return {
            "CLIP Prompt": state.get("clip_prompt") or state.get("evaluation_prompt"),
            "PickScore Prompt": state.get("pickscore_prompt"),
            "VLM Judge Prompt": state.get("vlm_judge_prompt"),
            "Metric Routing": result.get("metric_routing") or state.get("metric_prompts"),
            "Metric Summary": result.get("metric_summary"),
        }

    def _generation_routing_preview(self, state):
        plan = state.get("generation_plan") or {}
        return {
            "provider": state.get("generation_provider") or plan.get("provider"),
            "generation_mode": state.get("generation_mode") or plan.get("generation_mode"),
            "generation_config": state.get("generation_config"),
            "prompt_length": state.get("prompt_length"),
            "model_id": state.get("model_id"),
            "device": state.get("device"),
            "dtype": state.get("dtype"),
            "cfg": state.get("cfg") if state.get("cfg") is not None else plan.get("cfg"),
            "strength": (
                state.get("strength")
                if state.get("strength") is not None
                else plan.get("strength")
            ),
            "steps": state.get("steps") or plan.get("steps"),
            "scheduler": state.get("scheduler") or plan.get("scheduler"),
            "resolution": state.get("resolution") or plan.get("resolution"),
            "future_hooks": state.get("future_hooks") or plan.get("future_hooks"),
            "ip_adapter_status": state.get("ip_adapter_status"),
            "ip_adapter_enabled": state.get("ip_adapter_enabled"),
            "ip_adapter_loaded": state.get("ip_adapter_loaded"),
            "ip_adapter_repo_id": state.get("ip_adapter_repo_id"),
            "ip_adapter_subfolder": state.get("ip_adapter_subfolder"),
            "ip_adapter_weight_name": state.get("ip_adapter_weight_name"),
            "ip_adapter_scale": state.get("ip_adapter_scale"),
            "used_conditioning_fallback": state.get("used_conditioning_fallback"),
            "conditioning_fallback_reason": state.get("conditioning_fallback_reason"),
            "generation_is_mock": state.get("generation_is_mock"),
            "fallback_reason": state.get("fallback_reason"),
            "generation_error_type": state.get("generation_error_type"),
            "generation_error_repr": state.get("generation_error_repr"),
            "generation_error_stage": state.get("generation_error_stage"),
            "generation_error_traceback": state.get("generation_error_traceback"),
            "notes": state.get("generation_notes", []),
        }

    def _generation_preset_preview(self, state):
        preset = state.get("generation_preset") or (
            state.get("generation_config") or {}
        ).get("generation_preset") or {}
        return {
            "preset": preset.get("preset_name"),
            "strength": preset.get("sdxl_strength"),
            "ip_adapter_scale": preset.get("ip_adapter_scale"),
            "cfg": preset.get("cfg"),
            "steps": preset.get("steps"),
            "resolution": preset.get("resolution")
            or self._resolution_from_preset(preset),
            "reason": state.get("preset_reason") or preset.get("reason"),
            "environment_overrides": state.get("environment_overrides")
            or preset.get("environment_overrides", {}),
        }

    def _resolution_from_preset(self, preset):
        if not preset:
            return None
        width = preset.get("width")
        height = preset.get("height")
        if width and height:
            return f"{width}x{height}"
        return None

    def _style_transfer_preview(self, state):
        return {
            "style_program": state.get("style_program"),
            "selected_lora": state.get("selected_lora"),
            "lora_status": state.get("lora_status"),
            "ip_adapter": state.get("ip_adapter_status"),
            "controlnet": state.get("controlnet_status"),
            "controlnet_enabled": (
                state.get("controlnet_status") or {}
            ).get("enabled"),
            "controlnet_loaded": (
                state.get("controlnet_status") or {}
            ).get("loaded"),
            "controlnet_type": (
                state.get("controlnet_status") or {}
            ).get("type"),
            "control_image_path": (
                state.get("controlnet_status") or {}
            ).get("control_image_path"),
            "controlnet_fallback_reason": (
                state.get("controlnet_status") or {}
            ).get("fallback_reason"),
        }

    def _dino_metric_preview(self, state):
        result = self._evaluation_result(state) or {}
        metrics = result.get("metrics") or []
        dino = next(
            (
                item
                for item in metrics
                if isinstance(item, dict) and item.get("name") == "dino_identity"
            ),
            {},
        )
        return {
            "enabled": dino.get("enabled"),
            "score": dino.get("score"),
            "reason": dino.get("reason"),
            "used_fallback": dino.get("used_fallback"),
            "model": dino.get("model"),
        }

    def _vision_result_preview(self, vision_result):
        vision_result = vision_result or {}
        return {
            "model": vision_result.get("model"),
            "provider": vision_result.get("provider"),
            "used_fallback": vision_result.get("used_fallback"),
            "latency": vision_result.get("latency"),
            "caption": vision_result.get("caption"),
            "detailed_caption": vision_result.get("detailed_caption"),
            "detailed_description": vision_result.get("detailed_description"),
            "objects": vision_result.get("objects", []),
            "regions": vision_result.get("regions", []),
            "characters": vision_result.get("characters", []),
            "scene": vision_result.get("scene", {}),
            "style": vision_result.get("style", {}),
            "ocr": vision_result.get("ocr", []),
            "colors": vision_result.get("colors", {}),
            "composition": vision_result.get("composition", {}),
            "character_hints": vision_result.get("character_hints", {}),
            "style_hints": vision_result.get("style_hints", []),
            "composition_hints": vision_result.get("composition_hints", {}),
            "color_hints": vision_result.get("color_hints", {}),
        }

    def _vlm_summary(self, vision_result):
        vision_result = vision_result or {}
        return {
            "provider": vision_result.get("provider"),
            "model": vision_result.get("model"),
            "used_fallback": vision_result.get("used_fallback"),
            "latency": vision_result.get("latency"),
            "caption": vision_result.get("caption"),
            "detailed_caption": vision_result.get("detailed_caption"),
            "objects": vision_result.get("objects", []),
            "regions": vision_result.get("regions", []),
            "characters": vision_result.get("characters", []),
            "ocr": vision_result.get("ocr", []),
            "colors": vision_result.get("colors", {}),
            "composition": vision_result.get("composition", {}),
        }

    def _llm_summary(self, state):
        context_reasoning = state.get("context_reasoning") or {}
        critic_report = state.get("llm_prompt_critic_report") or {}
        optimizer_report = state.get("llm_optimizer_report") or {}
        hypothesis_reasoning = state.get("hypothesis_reasoning") or {}
        strategy_reasoning = state.get("strategy_reasoning") or {}
        sources = (
            state,
            context_reasoning,
            critic_report,
            optimizer_report,
            hypothesis_reasoning,
            strategy_reasoning,
        )
        provider = self._first(
            sources,
            ("llm_provider", "reasoning_provider"),
        )
        used_fallback = self._first(
            sources,
            ("llm_used_fallback", "reasoning_used_fallback", "used_fallback"),
        )
        raw_text = self._first(
            sources,
            ("llm_reasoning_raw_text", "raw_text"),
        )
        return {
            "llm_provider": provider,
            "llm_used_fallback": used_fallback,
            "llm_reasoning_raw_text": raw_text,
        }

    def _first(self, sources, keys):
        for source in sources:
            if not isinstance(source, dict):
                continue
            for key in keys:
                if key in source and source.get(key) not in (None, ""):
                    return source.get(key)
        return None

    def _safe(self, value):
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, dict):
            return {str(key): self._safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._safe(item) for item in value]
        return str(value)


