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
            "provider": self._safe(state.get("provider")),
            "planner_result": self._safe(state.get("planner_result")),
            "scene_plan": self._safe(state.get("scene_plan")),
            "memory_context": self._safe(state.get("memory_context")),
            "retrieved_context": self._safe(state.get("retrieved_context")),
            "context_program": self._safe(state.get("context_program")),
            "context_program_summary": self._safe(state.get("context_program_summary")),
            "context_program_version": self._safe(state.get("context_program_version")),
            "context_validation": self._safe(state.get("context_validation")),
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
            "optimization_report": self._safe(state.get("optimization_report")),
            "llm_optimizer_report": self._safe(state.get("llm_optimizer_report")),
            "provider_prompt": self._safe(state.get("provider_prompt")),
            "provider_negative_prompt": self._safe(state.get("provider_negative_prompt")),
            "evaluation_prompt": self._safe(state.get("evaluation_prompt")),
            "initial_output_image_path": self._safe(state.get("output_image_path")),
            "initial_score": self._safe(state.get("score")),
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
        self._append_block(lines, "SCENE PLAN", state.get("scene_plan"))
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
        self._append_block(lines, "OPTIMIZED PROMPT", state.get("optimized_prompt"))
        self._append_block(lines, "PROVIDER PROMPT", state.get("provider_prompt"))
        self._append_block(lines, "NEGATIVE PROMPT", state.get("provider_negative_prompt") or state.get("negative_prompt"))
        self._append_block(
            lines,
            "EVALUATION",
            {
                "score": state.get("score"),
                "retry": state.get("retry_needed"),
                "best_score": state.get("best_score"),
            },
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
