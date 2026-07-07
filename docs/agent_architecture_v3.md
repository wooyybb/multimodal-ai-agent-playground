# Agent Architecture v3

## Why Refactor?

The project grew through many sprints, so many files were named as agents. That was useful while building features, but it made the framework look more complex than it is.

v3 refactors the explanation from many small agents into five top-level agents. The code still uses the same modules, but the architecture is now easier to explain:

```text
Reference Understanding
-> Style Transfer Planning
-> Reference-aware Generation
-> Multi-Metric Evaluation
-> Reflection and Adaptive Replanning
```

## 5-Agent Flow

```text
User Request + Reference Image
  |
  v
Understanding Agent
  |
  v
Planning Agent
  |
  v
Generation Agent
  |
  v
Evaluation Agent
  |
  v
Reflection Agent
  |
  +--> Adaptive update / optional retry
```

## Agent vs Module

**Agent** means a higher-level unit responsible for a goal, decision, tool-use, and feedback loop.

**Module** means a lower-level component that performs one specific function inside an agent.

For example, `ReferenceImageParser` is important, but it is a module inside the Understanding Agent. `PromptCompiler` is a module inside the Generation Agent. `StrategySelector` is a module inside the Reflection Agent.

## Mapping Table

| Top-level Agent | Responsibility | Internal Modules |
| --- | --- | --- |
| Understanding Agent | Understand reference image and visual identity. | VisionAgent, ReferenceImageParser, CharacterProgramBuilder |
| Planning Agent | Convert user intent into structured style transfer planning. | LLMStyleTransferPlanner, GoalPlanner, ScenePlanningAgent, StyleAgent, LayoutAgent, PoseAgent, ExpressionAgent, LightingAgent, NegativePromptAgent, SemanticPromptEngine, ConflictResolver, PromptSanitizer, PromptValidator |
| Generation Agent | Render provider-specific prompts and run generation. | PromptCompiler, ProviderRouter, ProviderPromptAdapter, GenerationPlanner, GenerationRouter, SDXL Provider, FLUX Provider, ReferenceConditioningPipeline, StylePresetManager |
| Evaluation Agent | Score output quality from multiple perspectives. | CLIPMetric, DINOIdentityMetric, PromptMetric, AestheticMetric, EvaluationAggregator |
| Reflection Agent | Analyze failure, choose strategy, adapt plan, and retry. | ReflectionAgent, SelfVerification, StrategySelector, AdaptivePlanner, RetryAgent, MemorySave, DebugReport |

## Physical File Structure v3.3

v3.3 compresses the codebase further. `agents/` now keeps only top-level agent entry files and the orchestrator. Lower-level implementation files live in `modules/`, and commonly used cross-cutting APIs are exposed through `core/`.

```text
agents/
  understanding_agent.py
  planning_agent.py
  generation_agent.py
  evaluation_agent.py
  reflection_agent.py
  orchestrator_agent.py

modules/
  understanding/
  planning/
  generation/
  evaluation/
  reflection/
  prompt/
  memory/

core/
  style_transfer_program.py
  semantic_prompt_engine.py
  reference_conditioning.py
  generation_router.py
  evaluation_runner.py
  debug_report.py
```

The old small `agents/*` compatibility wrappers were removed after Registry and Orchestrator imports were moved to `modules.*`. API, UI, benchmark, and workflow entry points still import only `OrchestratorAgent`, so the runtime contract remains stable.

## 1-Minute Interview Explanation

This project is a reference-aware multimodal AI Agent framework for style transfer. It is not just a prompt-to-image script. The Understanding Agent extracts visual context from the reference image. The Planning Agent turns the user's natural language request into a structured Style Transfer Program and Semantic Prompt Program. The Generation Agent renders provider-specific prompts and runs FLUX or SDXL Img2Img with optional IP-Adapter and ControlNet hooks. The Evaluation Agent scores the result with CLIP, DINO, prompt, and aesthetic metrics. The Reflection Agent analyzes failures and updates the plan for retry.

The important design choice is that LLMs do not directly write the final prompt. They help plan structured intent, and the framework renders, validates, evaluates, and debugs the workflow.

## Future Work

- Move more prompt helper internals behind `core.semantic_prompt_engine`.
- Add a visual dashboard grouped by the five agents.
- Expand `component_trace` into a richer execution graph.
