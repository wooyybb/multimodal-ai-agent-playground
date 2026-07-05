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
            "llm_provider": self._safe(self._llm_summary(state).get("llm_provider")),
            "llm_used_fallback": self._safe(
                self._llm_summary(state).get("llm_used_fallback")
            ),
            "llm_reasoning_raw_text": self._safe(
                self._llm_summary(state).get("llm_reasoning_raw_text")
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
            "provider_negative_prompt": self._safe(state.get("provider_negative_prompt")),
            "evaluation_prompt": self._safe(state.get("evaluation_prompt")),
            "evaluation_result": self._safe(self._evaluation_result(state)),
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
        self._append_block(lines, "PROVIDER PROMPT", state.get("provider_prompt"))
        self._append_block(lines, "NEGATIVE PROMPT", state.get("provider_negative_prompt") or state.get("negative_prompt"))
        self._append_block(
            lines,
            "EVALUATION",
            self._evaluation_preview(state),
        )
        self._append_block(lines, "AGENT TRACE", "\n".join(state.get("agent_trace", [])))
        return "\n".join(lines).strip() + "\n"

    def _append_block(self, lines, title, value):
        lines.append(f"========== {title} ==========")
        lines.append(self._to_text(value))
        lines.append("")

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

    def _compiled_prompt_package_preview(self, package):
        package = package or {}
        return {
            "provider": package.get("provider"),
            "positive_prompt": package.get("positive_prompt"),
            "negative_prompt": package.get("negative_prompt"),
            "prompt_blocks": package.get("prompt_blocks", {}),
            "compiler_notes": package.get("compiler_notes", []),
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

    def _evaluation_preview(self, state):
        result = self._evaluation_result(state) or {}
        metrics = result.get("metrics") or []
        metric_map = {item.get("name"): item for item in metrics if isinstance(item, dict)}
        return {
            "CLIP": metric_map.get("clip", {}),
            "Identity": metric_map.get("identity", {}),
            "Prompt": metric_map.get("prompt", {}),
            "Aesthetic": metric_map.get("aesthetic", {}),
            "Weighted": result.get("weighted_score", state.get("score")),
            "Summary": result.get("metric_summary"),
            "retry": state.get("retry_needed"),
            "best_score": state.get("best_score"),
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
            "characters": vision_result.get("characters", []),
            "scene": vision_result.get("scene", {}),
            "style": vision_result.get("style", {}),
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
            "characters": vision_result.get("characters", []),
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
