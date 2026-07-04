# Multimodal AI Agent Playground

**Context Engineering based Multi-Agent Framework for Multimodal Image Generation**

![Status](https://img.shields.io/badge/status-active_development-blue)
![Python](https://img.shields.io/badge/python-3.x-green)
![Framework](https://img.shields.io/badge/AI_Agent-Framework-purple)
![License](https://img.shields.io/badge/license-TODO-lightgrey)

Multimodal AI Agent Playground is a modular AI Agent framework that combines **Vision Understanding**, **Context Engineering**, **Prompt Engineering**, **Provider Routing**, **Generation**, **Evaluation**, **Reflection**, **Adaptive Planning**, and **Memory** into one inspectable image generation workflow.

The project is designed as an AI Agent Engineering portfolio project. Its purpose is not only to generate images, but to show how a multimodal AI system can be decomposed into agents, traced through state, evaluated, retried, and improved over time.

## Table of Contents

- [Why This Project?](#why-this-project)
- [Architecture](#architecture)
- [AI Agent Workflow](#ai-agent-workflow)
- [Core Features](#core-features)
- [Repository Structure](#repository-structure)
- [AI Engineering Concepts](#ai-engineering-concepts)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Example Workflow](#example-workflow)
- [Roadmap](#roadmap)
- [Screenshots](#screenshots)
- [Future Work](#future-work)
- [Documentation](#documentation)
- [License](#license)

## Why This Project?

Most image generation demos follow a simple path:

```text
Image / Text
-> Prompt
-> Generation
-> Done
```

This project treats image generation as an agentic workflow:

```text
Image / Text
-> Vision Understanding
-> Character Program
-> Goal Tree
-> LLM Context Reasoning
-> Context Program
-> Prompt Compiler
-> Generation
-> Evaluation
-> Self Verification
-> Reflection
-> Strategy Selection
-> Adaptive Planning
-> Retry
-> Memory
```

The result is a framework where every step can be inspected: what the system understood, what context it built, how it compiled prompts, which provider was selected, why a retry happened, and what was stored in memory.

## Architecture

```text
User
  |
  v
Vision Layer
  |
  v
Character Program
  |
  v
Goal Planning
  |
  v
Reasoning Layer
  |
  v
Context Program
  |
  v
Prompt Compiler
  |
  v
Provider Layer
  |
  v
Generation
  |
  v
Evaluation
  |
  v
Reflection
  |
  v
Adaptive Planning
  |
  v
Memory
  |
  v
Benchmark / Debug Report
```

The framework is intentionally layered. UI, API, planning, execution, tools, providers, memory, benchmarking, and debug reports are separated so each concern can evolve independently.

## AI Agent Workflow

```text
PlannerAgent
-> GoalPlanner
-> DynamicExecutionEngine
-> ToolRegistry
-> VisionAgent
-> CharacterProgramBuilder
-> LLMContextReasoner
-> ScenePlanningAgent
-> Character / Style / Layout / Pose / Expression / Lighting Agents
-> ContextProgramBuilder
-> ContextProgramValidator
-> PromptAssembler
-> PromptCritic
-> PromptOptimizer
-> ProviderRouter
-> PromptCompiler
-> ProviderPromptAdapter
-> AIModelService
-> GenerationAgent
-> EvaluationAgent
-> ReflectionAgent
-> SelfVerificationAgent
-> StrategySelector
-> AdaptivePlanner
-> RetryAgent
-> MemoryManager
```

## Core Features

| Area | Description |
| --- | --- |
| Vision Layer | Uses BLIP by default through a VLM adapter layer; prepared for Florence-2 and Qwen-VL style expansion. |
| Character Program | Parses caption and vision result into structured identity, appearance, style, pose, expression, colors, and identity rules. |
| Goal-oriented Planning | Builds a Goal Tree with main goal, sub-goals, priorities, and success criteria before execution planning. |
| Context Engineering | Converts user intent, caption, memory, retrieval, scene, layout, and provider constraints into a structured Context Program. |
| Execution Engine | Runs a planner-produced workflow through a registry-based dynamic execution engine. |
| Memory | Stores previous prompts, scores, reflections, retries, and output paths for future context retrieval. |
| Reflection | Analyzes evaluation results and produces improvement direction. |
| Self Verification | Checks goal satisfaction, prompt consistency, context consistency, and whether replanning is needed before adaptive planning. |
| Strategy Selection | Generates candidate strategies from reflection signals and selects the highest-scoring strategy. |
| Adaptive Planning | Turns reflection into re-planning before retry by updating context priorities and strategy. |
| Prompt Compiler | Converts provider-independent Context Program into provider-specific prompt packages. |
| Prompt Critic | Reviews prompt quality, missing sections, conflicts, and provider suitability. |
| Prompt Optimizer | Improves prompt structure based on critic feedback. |
| Provider Routing | Selects generation provider using provider capability config. |
| AI Model Service | Provides a provider abstraction layer for mock/OpenAI/Gemini/Claude/Ollama-style LLM calls. |
| FastAPI | Exposes the framework through REST endpoints and Swagger docs. |
| Gradio | Provides a local interactive demo UI. |
| Benchmark | Runs multiple prompts and stores comparable result JSON. |
| Debug Report | Saves run state, prompt preview, agent trace, and generated image copies for inspection. |

## Repository Structure

```text
agents/       Agent classes for planning, prompt orchestration, routing, critique, and retry
workflow/     Dynamic execution engine, AgentState, debug report, and pipeline facade
tools/        BLIP, FLUX, CLIP wrappers and VLM adapter providers
llm/          LLM client, AIModelService, mock provider, and provider skeletons
memory/       MemoryManager and run history
knowledge/    Knowledge and style retrieval resources
benchmark/    Benchmark runner, result JSON, and report generator
api/          FastAPI service layer
ui/           Gradio app
docs/         Architecture, roadmap, decisions, sprint book, prompts, and reviews
config/       Provider capability configuration
registry/     ToolRegistry for agent/tool dispatch
outputs/      Runtime outputs only; do not use as a curated demo archive
```

## AI Engineering Concepts

- [x] Context Engineering
- [x] Prompt Engineering
- [x] AI Agent
- [x] Execution Engine
- [x] Planner
- [x] Goal-oriented Planning
- [x] Reflection
- [x] Adaptive Planning
- [x] Tool Calling
- [x] Memory
- [x] Provider Routing
- [x] Prompt Compiler
- [x] Vision-Language Model Adapter
- [x] Benchmark
- [x] Debug Report

## Technology Stack

- Python
- PyTorch
- Transformers
- FastAPI
- Gradio
- Hugging Face
- BLIP
- FLUX
- CLIP
- GitHub
- Codex

## Installation

```bash
pip install -r requirements.txt
```

Create a local `.env` file for private tokens:

```text
HF_TOKEN=your_local_token_here
```

Never commit real API keys, Hugging Face tokens, `.env` files, or generated output folders.

Optional PowerShell examples:

```powershell
$env:VLM_PROVIDER="blip"
$env:LLM_PROVIDER="mock"
```

For OpenAI provider experiments:

```powershell
$env:OPENAI_API_KEY="your_key_here"
$env:LLM_PROVIDER="openai"
$env:OPENAI_MODEL="gpt-5.5"
```

## Quick Start

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

Run compile check:

```bash
python -m compileall agents tools workflow memory ui registry knowledge api benchmark llm
```

Run benchmark:

```bash
python -m benchmark.benchmark_runner
```

Run report generator:

```bash
python -m benchmark.report_generator
```

## Example Workflow

Example run trace:

```text
[PlannerAgent] Running...
[GoalPlanner] Running...
[ExecutionEngine] Starting dynamic execution...
[VisionAgent] Running...
[LLMContextReasoner] Running...
[ContextProgramBuilder] Running...
[ContextProgramValidator] Valid:
[PromptCompiler] Running...
[GenerationAgent] Running...
[EvaluationAgent] Score:
[ReflectionAgent] Running...
[SelfVerification] Running...
[StrategySelector] Generating strategies...
[AdaptivePlanner] Running...
[RetryAgent] Score below threshold. Retry needed.
[DebugReport] Report saved:
```

## Roadmap

| Release | Focus |
| --- | --- |
| v0.1 | Core multi-agent framework, BLIP/FLUX/CLIP workflow, memory, retry |
| v0.2 | Context Engineering, Context Program, validation, prompt compiler |
| v0.3 | Intelligence Layer, LLM client abstraction, AIModelService, adaptive planning |
| v1.0 | Production AI Agent Framework with deployment, dashboard, multi-session support |

## Screenshots

Placeholder: curated screenshots and selected demo images should live under `assets/demo/` in a future sprint.

Do not commit the full `outputs/` directory as a demo asset archive.

## Future Work

- Real OpenAI/Gemini/Claude provider hardening
- Multi-VLM integration beyond BLIP
- Reference image parsing
- Style transfer workflow
- Multi-provider generation comparison
- Docker and deployment setup
- Queue-based generation jobs
- Benchmark dashboard
- Multi-session memory

## Documentation

- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Development Log](docs/development_log.md)
- [Concepts](docs/concepts.md)
- [Prompt Engineering](docs/prompt_engineering.md)
- [Design Decisions](docs/design_decisions.md)
- [Interview Notes](docs/interview_notes.md)
- [AI Usage](docs/ai_usage.md)
- [Code Reviews](docs/code_reviews.md)
- [Meeting Log](docs/meeting_log.md)
- [Retrospective](docs/retrospective.md)
- [Sprint Book](docs/sprint_book/README.md)

## License

TODO: Add a project license before public release.
