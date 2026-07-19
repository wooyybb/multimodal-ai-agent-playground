from core.tool_plan_schema import ToolPlanSchema


class PlanValidator:
    FORBIDDEN_TOOL_NAMES = {
        "shell",
        "python",
        "python_eval",
        "eval",
        "exec",
        "delete",
        "remove_file",
        "rm",
    }

    def __init__(self, catalog, *, max_steps=12):
        self.catalog = catalog
        self.max_steps = max_steps

    def validate(self, tool_plan, state=None, *, replan=False):
        state = state or {}
        raw_steps = (tool_plan or {}).get("steps") if isinstance(tool_plan, dict) else []
        raw_step_count = len(raw_steps) if isinstance(raw_steps, list) else 0
        plan = ToolPlanSchema.normalize(tool_plan)
        errors = []
        warnings = []
        selected_tools = []
        seen = set()

        if plan.get("max_steps", self.max_steps) > self.max_steps:
            errors.append(
                f"max_steps {plan.get('max_steps')} exceeds limit {self.max_steps}"
            )

        steps = list(plan.get("steps") or [])
        if raw_step_count > self.max_steps:
            errors.append(f"step count {raw_step_count} exceeds limit {self.max_steps}")
        elif len(steps) > self.max_steps:
            errors.append(f"step count {len(steps)} exceeds limit {self.max_steps}")

        produced_state = set(state.keys())
        produced_state.update({"user_prompt", "image", "style_transfer_program"})
        has_generation = False
        has_prompt_rendering = False

        for step in steps:
            tool_name = str(step.get("tool") or "").strip()
            if not tool_name:
                errors.append(f"step {step.get('step_id')} has no tool")
                continue
            if tool_name.lower() in self.FORBIDDEN_TOOL_NAMES:
                errors.append(f"forbidden tool requested: {tool_name}")
                continue
            if not self.catalog.exists(tool_name):
                errors.append(f"tool is not in Tool Catalog: {tool_name}")
                continue

            tool = self.catalog.get(tool_name)
            allowed_key = "allowed_in_replan" if replan else "allowed_in_initial_plan"
            if not tool.get(allowed_key):
                errors.append(f"tool is not allowed in this plan phase: {tool_name}")

            if tool_name in seen:
                warnings.append(f"duplicate tool skipped: {tool_name}")
                continue
            selected_tools.append(tool_name)
            seen.add(tool_name)

            missing = [
                key
                for key in step.get("required_state", [])
                if key not in produced_state and not self._is_deferred_state(key)
            ]
            if missing:
                warnings.append(
                    f"{tool_name} requires state that may be produced later: {missing}"
                )

            if tool_name.startswith("generate_"):
                has_generation = True
                if not has_prompt_rendering:
                    errors.append("generation selected before provider prompt rendering")
            if tool_name in ("render_provider_prompt", "compile_semantic_prompt"):
                has_prompt_rendering = True

            if tool_name.startswith("evaluate_") or tool_name == "aggregate_evaluation":
                if not has_generation:
                    errors.append("evaluation selected before generation")

            produced_state.update(tool.get("produced_state") or [])

        normalized_plan = dict(plan)
        normalized_plan["steps"] = [
            step for step in steps if step.get("tool") in selected_tools
        ]
        execution_plan = self.catalog.to_execution_plan(normalized_plan)
        if not execution_plan:
            errors.append("validated plan produced no executable tools")

        valid = not errors
        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "fallback_used": not valid,
            "selected_tools": selected_tools,
            "execution_plan": execution_plan,
            "max_steps": self.max_steps,
        }

    def _is_deferred_state(self, key):
        return key in {
            "vision_result",
            "reference_image",
            "character_program",
            "context_program",
            "semantic_prompt_program",
            "provider_prompt",
            "reference_conditioning_package",
            "output_image_path",
            "evaluation_result",
            "reflection",
        }




