# Multimodal AI Agent Playground

**Layer-based AI Agent Framework for Multimodal Image Generation**

![Status](https://img.shields.io/badge/status-v1.0_RC1-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)
![Architecture](https://img.shields.io/badge/Architecture-Layer--based-purple)
![FastAPI](https://img.shields.io/badge/API-FastAPI-teal)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange)

## Project Overview

This project is not a collection of many agents for its own sake. It is a multimodal image generation framework organized into six layers:

1. Planning Layer
2. Context Layer
3. Generation Layer
4. Evaluation Layer
5. Reasoning Layer
6. Memory / Observability Layer

The framework turns user input and reference images into structured planning data, builds a provider-independent Context Program, compiles provider-specific prompts, generates images, evaluates outputs, reasons about failures, and records each run for debugging and comparison.

## Why This Project?

Most image generation demos stop at:

```text
User Prompt -> Image Generation -> Result
```

This project treats image generation as an inspectable AI Agent workflow:

```text
Understand input
-> Plan goals and visual context
-> Build Context Program
-> Compile provider prompt
-> Generate image
-> Evaluate with multiple metrics
-> Reflect and re-plan
-> Save memory and debug report
```

The purpose is to show framework-level engineering: separation of responsibility, provider abstraction, context engineering, evaluation, fallback design, and observability.

## Layer-based Architecture

```text
User Input
  |
  v
Planning Layer
  - PlannerAgent
  - GoalPlanner
  - ReferenceImageParser
  - CharacterProgramBuilder
  |
  v
Context Layer
  - ContextProgramBuilder
  - ContextProgramValidator
  - PromptAssembler
  - PromptCompiler
  |
  v
Generation Layer
  - ProviderRouter
  - ProviderPromptAdapter
  - GenerationAgent
  |
  v
Evaluation Layer
  - EvaluationAgent
  - EvaluationAggregator
  - CLIP / Identity / Prompt / Aesthetic Metrics
  |
  v
Reasoning Layer
  - ReflectionAgent
  - SelfVerificationAgent
  - StrategySelector
  - AdaptivePlanner
  |
  v
Memory / Observability Layer
  - MemoryManager
  - DebugReportManager
  - BenchmarkRunner
  - ReportGenerator
```

## End-to-End Workflow

```text
Image / User Prompt
-> Planning Layer
-> Context Layer
-> Generation Layer
-> Evaluation Layer
-> Reasoning Layer
-> Memory / Observability Layer
```

The internal implementation still uses individual Python classes, but the project is explained and maintained through layer ownership.

## Core Layers

| Layer | Role | Representative Components |
| --- | --- | --- |
| Planning | Interpret user intent, image references, goals, scene, and character identity. | PlannerAgent, GoalPlanner, ReferenceImageParser |
| Context | Convert planning output into Context Program and provider-independent prompt structures. | ContextProgramBuilder, PromptCompiler |
| Generation | Select provider, adapt prompt, and generate image. | ProviderRouter, ProviderPromptAdapter, GenerationAgent |
| Evaluation | Score generated output with multiple metrics. | EvaluationAgent, EvaluationAggregator |
| Reasoning | Reflect, verify, select strategy, and adapt plan. | ReflectionAgent, StrategySelector, AdaptivePlanner |
| Memory / Observability | Save history, debug reports, benchmark outputs, and prompt previews. | MemoryManager, DebugReportManager, BenchmarkRunner |

## Key Features

- Layer-based AI Agent architecture
- DynamicExecutionEngine and ToolRegistry
- BLIP default VLM with Florence/Qwen adapter skeletons
- Reference Image Parser and Character Program
- Context Program and Context Validator
- Prompt Compiler and Provider Prompt Adapter
- FLUX-oriented generation path
- Multi-Metric Evaluation with CLIP and rule-based metrics
- Reflection, Self Verification, Strategy Selection, Adaptive Planning
- Optional LLM reasoning with rule fallback
- Memory, Debug Report, Benchmark Runner, Report Generator
- Gradio UI and FastAPI service layer

## Repository Structure

```text
agents/       Agent classes grouped conceptually by planning, context, reasoning, and generation roles
workflow/     DynamicExecutionEngine, AgentState, debug reports, pipeline facade
tools/        BLIP, FLUX, CLIP, and VLM adapter tools
llm/          LLM client, reasoner router, AIModelService, provider skeletons
evaluation/   Metric abstraction and EvaluationAggregator
memory/       MemoryManager and run history
knowledge/    Retrieval knowledge and style library resources
api/          FastAPI service layer
ui/           Gradio interface
benchmark/    Benchmark runner and report generator
docs/         Architecture, layer map, roadmap, sprint book, prompts, interview notes
outputs/      Runtime output directory; do not commit generated outputs
```

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Gradio:

```bash
python main.py
```

Run FastAPI:

```bash
uvicorn api.app:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Run benchmark:

```bash
python -m benchmark.benchmark_runner
```

Run report generator:

```bash
python -m benchmark.report_generator
```

Run with Docker:

```bash
docker compose up --build
```

FastAPI: `http://127.0.0.1:8000/docs`

Gradio: `http://127.0.0.1:7860`

Stop Docker services:

```bash
docker compose down
```

## Debug Report / Benchmark

Each run can save:

- `report.json`: machine-readable state snapshot
- `prompt_preview.txt`: human-readable prompt lifecycle and agent trace
- output image references
- evaluation scores and retry information

Benchmark results are saved under `benchmark/results/`. Do not commit runtime outputs or API keys.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `HF_TOKEN` | Hugging Face access token for model/provider access. |
| `OPENAI_API_KEY` | Optional OpenAI key for LLM reasoning experiments. |
| `LLM_PROVIDER` | `rule`, `mock`, or `openai`; default behavior remains rule/fallback oriented. |
| `VLM_PROVIDER` | `blip`, `florence`, or `qwen`; BLIP is the default. |

## Current Limitations

- BLIP is the default VLM; Florence/Qwen adapters currently use BLIP fallback.
- FLUX is the current generation provider path.
- OpenAI reasoning is optional and falls back to rule-based behavior.
- Some reasoning and evaluation steps are intentionally rule-based for stability.
- Image quality depends on external model/provider behavior.

## Roadmap

| Release | Focus |
| --- | --- |
| v0.1 | Core multimodal pipeline |
| v0.2 | Multi-agent orchestration and registry |
| v0.3 | Context Engineering and Prompt Compiler |
| v0.4 | Reasoning loop and provider abstraction |
| v0.5 | Evaluation, debug reports, benchmark |
| v1.0 RC1 | Layer-based architecture cleanup |
| v1.0 | Demo polish, CI, deployment-ready documentation |

## Portfolio Highlights

This project demonstrates:

- AI Agent Architecture
- Context Engineering
- Prompt Engineering
- Multimodal AI workflow design
- Provider abstraction and fallback design
- Multi-metric evaluation
- Backend API and UI integration
- Debuggable AI system design
- Framework refactoring from feature-based agents into layer-based architecture

## Documentation

- [Architecture](docs/architecture.md)
- [Layer Map](docs/layer_map.md)
- [Project Summary](docs/project_summary.md)
- [Demo Guide](docs/demo_guide.md)
- [Interview Notes](docs/interview_notes.md)
- [Roadmap](docs/roadmap.md)
- [v1.0 RC1 Release Notes](docs/release_notes_v1_rc1.md)

## License

TODO: Add a project license before public release.
