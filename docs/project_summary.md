# Project Summary

## Project Identity

Multimodal AI Agent Playground is a **Reference-aware Multimodal AI Agent Framework for Style Transfer**.

The project is designed to extend multimodal generation research into an inspectable AI system: it understands a reference image, plans a style transfer request as structured data, renders provider-specific prompts, generates with reference-aware conditioning, evaluates the result, and adaptively replans.

## Problem Definition

Simple prompt-to-image demos are hard to debug. When the output is poor, it is unclear whether the issue came from reference understanding, prompt construction, provider limitations, evaluation, or retry logic.

This project separates those responsibilities into five top-level agents:

1. Understanding Agent
2. Planning Agent
3. Generation Agent
4. Evaluation Agent
5. Reflection Agent

Existing smaller agents are treated as modules inside these higher-level agents.

The runtime `OrchestratorAgent` is a coordinator rather than a sixth agent. It starts the workflow, asks the Planning Agent for an execution plan, builds the initial state, and hands execution to `DynamicExecutionEngine`. Module construction and ToolRegistry registration are centralized in `registry/tool_registry_factory.py`.

v3.5 keeps that boundary explicit: public output shaping lives in `core/result_builder.py`, common orchestration keys live in `core/state_keys.py`, and Planning Agent keeps a reserved Requirement Parser slot for future long requirement parsing.

## Core Flow

```text
Reference Understanding
-> Style Transfer Planning
-> Reference-aware Generation
-> Multi-Metric Evaluation
-> Reflection and Adaptive Replanning
```

## System Structure

| Agent | Responsibility | Representative Modules |
| --- | --- | --- |
| Understanding Agent | Understand the reference image and extract structured visual context. | VisionAgent, ReferenceImageParser, CharacterProgramBuilder |
| Planning Agent | Convert user intent into Style Transfer Program, semantic prompt program, constraints, and validation results. | LLMStyleTransferPlanner, GoalPlanner, ScenePlanningAgent, SemanticPromptEngine, ConflictResolver, PromptSanitizer, PromptValidator |
| Generation Agent | Render provider-specific prompts and run reference-aware generation. | PromptCompiler, ProviderRouter, ProviderPromptAdapter, GenerationRouter, SDXL/FLUX providers, StylePresetManager, ReferenceConditioningPipeline |
| Evaluation Agent | Score generated output with multiple metrics. | CLIPMetric, DINOIdentityMetric, PromptMetric, AestheticMetric, EvaluationAggregator |
| Reflection Agent | Analyze failures, choose strategies, adapt the next plan, retry, and record observability data. | ReflectionAgent, SelfVerification, StrategySelector, AdaptivePlanner, RetryAgent, DebugReport |

## Key Implementation Points

- Provider-independent Vision Layer with BLIP default and Florence fallback.
- Planning Agent has a reserved Requirement Parser slot for future long prompt to JSON program parsing.
- Orchestrator is thin; ToolRegistryFactory owns module creation and grouped registration.
- Result Builder preserves the public pipeline response shape outside Orchestrator.
- Style Transfer Program as structured planning output instead of raw prompt text.
- Semantic Prompt Engine for merge, conflict resolution, validation, and provider-specific rendering.
- SDXL Img2Img quality route with optional IP-Adapter and ControlNet hooks.
- Multi-metric evaluation using CLIP, DINO identity, prompt consistency, and aesthetic heuristics.
- Debug reports that store state, prompt lifecycle, provider routing, evaluation result, and v3 agent traces.
- FastAPI, Gradio, benchmark, and report generation as infrastructure around the same core pipeline.

## Technology Stack

- Python
- PyTorch
- Transformers
- Hugging Face
- BLIP / Florence adapter skeleton
- Diffusers SDXL Img2Img
- FLUX fast provider path
- CLIP and DINO-based evaluation
- FastAPI
- Gradio
- Docker
- Git/GitHub
- Codex-assisted development

## Current Limitations

- BLIP remains the default VLM.
- Florence is optional and falls back to BLIP when unavailable.
- FLUX is the default fast generation route.
- SDXL quality mode requires Diffusers dependencies, model access, and a reference image.
- IP-Adapter and ControlNet are optional hooks with fallback behavior.
- Some planning, reflection, and evaluation logic remains rule-based for predictable local execution.

## Future Improvements

- Stronger real VLM parsing.
- More robust LLM planner schema validation.
- Queue-based service execution.
- Benchmark dashboard.
- Multi-session memory.
- CI smoke tests and public demo release.
