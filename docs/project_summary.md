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

The design goal is to separate the workflow into clear layers:

1. Planning Layer
2. Context Layer
3. Generation Layer
4. Evaluation Layer
5. Reasoning Layer
6. Memory / Observability Layer

This lets the project stay understandable even as the number of agents grows.

## Layer-based Structure

The Planning Layer interprets the user request, image reference, goal tree, scene plan, and character identity.

The Context Layer converts planning output into Context Program and provider-independent prompt structures.

The Generation Layer selects the provider, adapts the prompt, and runs image generation.

The Evaluation Layer scores output with CLIP and additional rule-based metrics.

The Reasoning Layer performs reflection, self verification, strategy selection, adaptive planning, and retry decisions.

The Memory / Observability Layer saves run history, debug reports, benchmark results, and prompt previews.

## Core Implementation

- `DynamicExecutionEngine` runs the planned workflow.
- `ToolRegistry` isolates step names from concrete classes.
- `ContextProgramBuilder` and `PromptCompiler` separate semantic context from provider prompts.
- `ProviderRouter` and `ProviderPromptAdapter` isolate generation provider details.
- `EvaluationAggregator` combines multiple metrics into an explainable score.
- `DebugReportManager` captures state, prompts, traces, metrics, and output paths.
- `BenchmarkRunner` and `ReportGenerator` support repeatable comparison.

## Technology Stack

- Python
- PyTorch
- Transformers
- Hugging Face
- BLIP
- FLUX
- CLIP
- FastAPI
- Gradio
- Docker
- Git/GitHub
- Codex-assisted development

## Current Limitations

- BLIP remains the default VLM.
- Florence/Qwen adapters are prepared as skeletons with fallback.
- FLUX is the current generation provider path.
- Some reasoning remains rule-based by default.
- External provider quality and latency can affect final image quality.

## Future Improvements

- CI and Docker smoke tests.
- Queue-based async generation.
- Multi-session memory.
- Benchmark dashboard.
- Stronger VLM and VLM Judge integration.
- More explicit AgentState organization by layer.
