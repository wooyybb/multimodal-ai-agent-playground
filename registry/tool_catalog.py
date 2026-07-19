class ToolCatalog:
    def __init__(self):
        self._tools = self._build_tools()

    def tools_for_llm(self, *, replan=False):
        key = "allowed_in_replan" if replan else "allowed_in_initial_plan"
        return [
            self._public_schema(tool)
            for tool in self._tools.values()
            if tool.get(key)
        ]

    def get(self, name):
        return self._tools.get(name)

    def exists(self, name):
        return name in self._tools

    def aliases(self):
        return list(self._tools.keys())

    def actual_steps_for(self, name):
        tool = self.get(name) or {}
        return list(tool.get("actual_steps") or [])

    def to_execution_plan(self, tool_plan):
        execution_plan = []
        seen = set()
        for step in tool_plan.get("steps") or []:
            for actual_step in self.actual_steps_for(step.get("tool")):
                if actual_step in seen:
                    continue
                execution_plan.append(actual_step)
                seen.add(actual_step)
        return execution_plan

    def _public_schema(self, tool):
        return {
            "name": tool["name"],
            "agent_group": tool["agent_group"],
            "description": tool["description"],
            "required_state": tool["required_state"],
            "produced_state": tool["produced_state"],
            "allowed_in_initial_plan": tool["allowed_in_initial_plan"],
            "allowed_in_replan": tool["allowed_in_replan"],
            "cost": tool["cost"],
        }

    def _tool(
        self,
        name,
        agent_group,
        description,
        required_state,
        produced_state,
        actual_steps,
        *,
        initial=True,
        replan=True,
        cost="low",
    ):
        return {
            "name": name,
            "agent_group": agent_group,
            "description": description,
            "required_state": required_state,
            "produced_state": produced_state,
            "actual_steps": actual_steps,
            "allowed_in_initial_plan": initial,
            "allowed_in_replan": replan,
            "cost": cost,
        }

    def _build_tools(self):
        tools = [
            self._tool(
                "parse_requirement",
                "planning",
                "Parse long user requirement into Style Transfer Program.",
                ["user_prompt"],
                ["style_transfer_program"],
                ["goal_planner", "memory_load"],
                replan=False,
            ),
            self._tool(
                "understand_reference",
                "understanding",
                "Run provider-independent vision on the reference image.",
                ["image"],
                ["vision_result"],
                ["vision"],
                cost="medium",
            ),
            self._tool(
                "parse_reference",
                "understanding",
                "Parse structured vision output into reference image context.",
                ["vision_result"],
                ["reference_image"],
                ["reference_image_parser"],
            ),
            self._tool(
                "build_character_program",
                "understanding",
                "Build identity and appearance program from reference context.",
                ["reference_image"],
                ["character_program"],
                ["character_program_builder"],
            ),
            self._tool(
                "prepare_context",
                "planning",
                "Run planning components and build the Context Program.",
                ["user_prompt"],
                ["context_program"],
                [
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
                ],
                cost="medium",
            ),
            self._tool(
                "build_style_transfer_program",
                "planning",
                "Finalize style transfer program for semantic compilation.",
                ["style_transfer_program"],
                ["final_style_transfer_program"],
                ["prompt_compiler"],
            ),
            self._tool(
                "compile_semantic_prompt",
                "planning",
                "Compile the style transfer program into semantic prompt sections.",
                ["context_program"],
                ["semantic_prompt_program"],
                ["prompt_compiler"],
            ),
            self._tool(
                "render_provider_prompt",
                "generation",
                "Render model-specific prompt package from semantic prompt program.",
                ["semantic_prompt_program"],
                ["provider_prompt"],
                ["provider_router", "provider_prompt_adapter"],
            ),
            self._tool(
                "generate_flux",
                "generation",
                "Run the fast FLUX-compatible generation route.",
                ["provider_prompt"],
                ["output_image_path"],
                ["generation"],
                cost="high",
            ),
            self._tool(
                "generate_sdxl_img2img",
                "generation",
                "Run SDXL Img2Img quality generation when configured.",
                ["provider_prompt", "image"],
                ["output_image_path"],
                ["generation"],
                cost="high",
            ),
            self._tool(
                "generate_sdxl_with_ip_adapter",
                "generation",
                "Run SDXL with optional IP-Adapter conditioning.",
                ["provider_prompt", "reference_conditioning_package"],
                ["output_image_path"],
                ["generation"],
                cost="high",
            ),
            self._tool(
                "generate_sdxl_with_controlnet",
                "generation",
                "Run SDXL with optional ControlNet structure conditioning.",
                ["provider_prompt", "reference_conditioning_package"],
                ["output_image_path"],
                ["generation"],
                cost="high",
            ),
            self._tool(
                "evaluate_clip",
                "evaluation",
                "Evaluate text-image semantic alignment through the metric runner.",
                ["output_image_path"],
                ["evaluation_result"],
                ["evaluation"],
                cost="medium",
            ),
            self._tool(
                "evaluate_dino",
                "evaluation",
                "Evaluate reference-generated visual identity through the metric runner.",
                ["output_image_path", "image"],
                ["evaluation_result"],
                ["evaluation"],
                cost="medium",
            ),
            self._tool(
                "aggregate_evaluation",
                "evaluation",
                "Aggregate available metrics into a weighted evaluation result.",
                ["output_image_path"],
                ["evaluation_result"],
                ["evaluation"],
                cost="medium",
            ),
            self._tool(
                "analyze_failure",
                "reflection",
                "Reflect on evaluation result and classify failure type.",
                ["evaluation_result"],
                ["reflection"],
                ["reflection"],
            ),
            self._tool(
                "adjust_generation_strategy",
                "reflection",
                "Apply bounded adaptive planning and retry decision.",
                ["reflection"],
                ["adaptive_plan", "retry_needed"],
                [
                    "self_verification",
                    "strategy_selector",
                    "adaptive_planner",
                    "retry",
                    "memory_save",
                ],
                cost="medium",
            ),
        ]
        return {tool["name"]: tool for tool in tools}



