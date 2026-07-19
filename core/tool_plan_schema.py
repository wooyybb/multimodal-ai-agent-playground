class ToolPlanSchema:
    DEFAULT_MAX_STEPS = 12
    DEFAULT_STOP_CONDITIONS = [
        "generation_success",
        "evaluation_threshold_met",
    ]

    REQUIRED_STEP_KEYS = {
        "step_id": 0,
        "tool": "",
        "reason": "",
        "required_state": [],
        "expected_output": [],
        "arguments": {},
    }

    @classmethod
    def normalize(cls, payload, *, fallback_goal="Reference-aware style transfer"):
        payload = payload if isinstance(payload, dict) else {}
        steps = payload.get("steps") if isinstance(payload.get("steps"), list) else []
        normalized_steps = []
        for index, step in enumerate(steps[: cls.DEFAULT_MAX_STEPS], start=1):
            if not isinstance(step, dict):
                continue
            normalized_step = dict(cls.REQUIRED_STEP_KEYS)
            normalized_step.update(step)
            normalized_step["step_id"] = int(normalized_step.get("step_id") or index)
            normalized_step["tool"] = str(normalized_step.get("tool") or "").strip()
            normalized_step["required_state"] = cls._list_value(
                normalized_step.get("required_state")
            )
            normalized_step["expected_output"] = cls._list_value(
                normalized_step.get("expected_output")
            )
            if not isinstance(normalized_step.get("arguments"), dict):
                normalized_step["arguments"] = {}
            if normalized_step["tool"]:
                normalized_steps.append(normalized_step)

        return {
            "goal": str(payload.get("goal") or fallback_goal),
            "selected_strategy": str(
                payload.get("selected_strategy")
                or "bounded_reference_aware_style_transfer"
            ),
            "steps": normalized_steps,
            "stop_conditions": cls._list_value(
                payload.get("stop_conditions") or cls.DEFAULT_STOP_CONDITIONS
            ),
            "max_steps": int(payload.get("max_steps") or cls.DEFAULT_MAX_STEPS),
            "confidence": cls._float_value(payload.get("confidence"), 0.0),
        }

    @classmethod
    def rule_plan(cls, goal="Reference-aware style transfer"):
        return cls.normalize(
            {
                "goal": goal,
                "selected_strategy": "rule_safe_full_pipeline",
                "steps": [
                    {
                        "step_id": 1,
                        "tool": "parse_requirement",
                        "reason": "Convert the user requirement into a structured program.",
                        "required_state": ["user_prompt"],
                        "expected_output": ["style_transfer_program"],
                    },
                    {
                        "step_id": 2,
                        "tool": "understand_reference",
                        "reason": "Read the reference image when one is available.",
                        "required_state": ["image"],
                        "expected_output": ["vision_result"],
                    },
                    {
                        "step_id": 3,
                        "tool": "parse_reference",
                        "reason": "Convert vision output into reference context.",
                        "required_state": ["vision_result"],
                        "expected_output": ["reference_image"],
                    },
                    {
                        "step_id": 4,
                        "tool": "build_character_program",
                        "reason": "Extract identity and appearance constraints.",
                        "required_state": ["reference_image"],
                        "expected_output": ["character_program"],
                    },
                    {
                        "step_id": 5,
                        "tool": "prepare_context",
                        "reason": "Build planning components and the Context Program.",
                        "required_state": ["user_prompt"],
                        "expected_output": ["context_program"],
                    },
                    {
                        "step_id": 6,
                        "tool": "compile_semantic_prompt",
                        "reason": "Create semantic prompt inputs for provider rendering.",
                        "required_state": ["context_program"],
                        "expected_output": ["semantic_prompt_program"],
                    },
                    {
                        "step_id": 7,
                        "tool": "render_provider_prompt",
                        "reason": "Render provider-specific generation and evaluation prompts.",
                        "required_state": ["semantic_prompt_program"],
                        "expected_output": ["provider_prompt"],
                    },
                    {
                        "step_id": 8,
                        "tool": "generate_sdxl_img2img",
                        "reason": "Generate with the configured provider route.",
                        "required_state": ["provider_prompt"],
                        "expected_output": ["output_image_path"],
                    },
                    {
                        "step_id": 9,
                        "tool": "aggregate_evaluation",
                        "reason": "Evaluate generated output with available metrics.",
                        "required_state": ["output_image_path"],
                        "expected_output": ["evaluation_result"],
                    },
                    {
                        "step_id": 10,
                        "tool": "analyze_failure",
                        "reason": "Reflect on quality and prepare bounded adaptation if needed.",
                        "required_state": ["evaluation_result"],
                        "expected_output": ["reflection"],
                    },
                    {
                        "step_id": 11,
                        "tool": "adjust_generation_strategy",
                        "reason": "Apply bounded retry and save observability data.",
                        "required_state": ["reflection"],
                        "expected_output": ["retry_needed"],
                    },
                ],
                "max_steps": cls.DEFAULT_MAX_STEPS,
                "confidence": 0.72,
            },
            fallback_goal=goal,
        )

    @staticmethod
    def _list_value(value):
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value if item not in (None, "")]
        return [str(value)]

    @staticmethod
    def _float_value(value, default):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
