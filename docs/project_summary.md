# Project Summary

## Project Purpose

Multimodal AI Agent Playground is an AI Agent Engineering project for multimodal image generation. The project demonstrates how image generation can be organized as a layer-based framework rather than a simple prompt-to-image script.

## Problem Definition

Many image generation demos are difficult to inspect because prompt creation, model invocation, evaluation, and retry logic are mixed together. When the output is poor, it is hard to answer:

- What did the system understand from the input image?
- Which goals were prioritized?
- How was context converted into a provider prompt?
- Why did the system retry or re-plan?
- How can runs be compared later?

## Design Goal

The design goal is to keep the framework understandable through five responsibilities:

1. Planning Layer
2. Context Layer
3. Generation Layer
4. Evaluation Layer
5. Infrastructure Layer

This keeps the project understandable even as the number of internal agents grows.

## Layer-based Structure

The Planning Layer interprets the user request, image reference, goal tree, scene plan, and character identity.

In v1.1, the Planning Layer includes a provider-independent Vision Layer. `VisionAgent` uses `VLMRouter` to select BLIP by default, Florence2 when requested, or planned Qwen2.5-VL support. All providers return the same structured `vision_result`, so the Reference Image Parser can read `characters`, `objects`, `style`, `colors`, and `composition` before falling back to caption parsing.

The Context Layer converts planning output into Context Program and provider-independent prompt structures.

The Generation Layer selects the provider, adapts the prompt, and runs image generation.

The Evaluation Layer scores output with CLIP and additional rule-based metrics, then performs reflection, strategy selection, adaptive planning, and retry decisions.

The Infrastructure Layer saves run history, debug reports, benchmark results, prompt previews, and exposes FastAPI/Gradio access.

## Core Implementation

- `DynamicExecutionEngine` runs the planned workflow.
- `ToolRegistry` isolates step names from concrete classes.
- `ContextProgramBuilder` and `PromptCompiler` separate semantic context from provider prompts.
- `ProviderRouter` and `ProviderPromptAdapter` isolate generation provider details.
- `EvaluationAggregator` combines multiple metrics into an explainable score.
- Adaptive planning and retry are treated as part of the Evaluation Layer's feedback loop.
- `DebugReportManager` captures state, prompts, traces, metrics, and output paths.
- `BenchmarkRunner` and `ReportGenerator` support repeatable comparison.
- The LLM Layer supports optional OpenAI structured JSON reasoning while preserving rule/mock fallback behavior.

## Technology Stack

- Python
- PyTorch
- Transformers
- Hugging Face
- BLIP
- Florence2 adapter with BLIP fallback
- FLUX
- CLIP
- FastAPI
- Gradio
- Docker
- Optional OpenAI reasoning
- Git/GitHub
- Codex-assisted development

## Current Limitations

- BLIP remains the default VLM.
- Florence2 can be selected through `VLM_PROVIDER=florence2`; if the model cannot load, the system falls back to BLIP and records `used_fallback=true`.
- Qwen2.5-VL is planned and currently uses BLIP fallback.
- FLUX is the current generation provider path.
- Some reasoning remains rule-based by default.
- OpenAI reasoning is optional and falls back automatically when no API key is available or JSON parsing fails.
- External provider quality and latency can affect final image quality.

## Future Improvements

- CI and Docker smoke tests.
- Queue-based async generation.
- Multi-session memory.
- Benchmark dashboard.
- Stronger VLM output parsing and VLM Judge integration.
- More explicit AgentState organization by layer.
