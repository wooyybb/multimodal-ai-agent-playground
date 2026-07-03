# Multimodal AI Agent Playground

Multimodal AI Agent Playground is a Python-based multi-agent image generation framework. It connects planning, retrieval, context engineering, prompt engineering, provider routing, generation, evaluation, reflection, retry, memory, debugging, and benchmark reporting into one inspectable workflow.

The project is built as an AI Agent Engineering portfolio project. The goal is not only to generate images, but to show how an agent system can be decomposed into clear roles, traced, evaluated, and improved over many sprints.

## Table of Contents

- [Project Goal](#project-goal)
- [Architecture Diagram](#architecture-diagram)
- [Pipeline](#pipeline)
- [Core Features](#core-features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Roadmap](#project-roadmap)
- [Screenshots](#screenshots)
- [Documentation](#documentation)
- [Future Work](#future-work)
- [License](#license)

## Project Goal

- Build a modular multi-agent framework for multimodal image generation.
- Separate planning, context building, prompt assembly, provider adaptation, generation, evaluation, retry, and memory.
- Keep every agent role small enough to explain in interviews and debug reports.
- Support real model integrations where available while keeping fallback paths for development.

## Architecture Diagram

```text
User
-> Gradio UI / FastAPI
-> LLMClient / MockLLM
-> AIModelService
-> LLMContextReasoner
-> PlannerAgent
-> DynamicExecutionEngine
-> ToolRegistry
-> VisionAgent
-> Memory Retrieval
-> Knowledge Retrieval
-> ScenePlanningAgent
-> Character / Style / Layout / Pose / Expression / Lighting / Negative Agents
-> ContextProgramBuilder
-> ContextProgramValidator
-> PromptAssembler
-> PromptCritic
-> LLMPromptCritic
-> PromptOptimizer / LLMPromptOptimizer interface
-> ProviderRouter
-> PromptCompiler
-> ProviderPromptAdapter
-> GenerationAgent
-> EvaluationAgent
-> ReflectionAgent / RetryAgent
-> MemoryManager
-> DebugReport / BenchmarkReport
```

## Pipeline

1. User uploads an image and enters a text request.
2. `LLMContextReasoner` creates a mock semantic planning layer from user intent.
3. `PlannerAgent` creates an execution plan.
4. `DynamicExecutionEngine` runs registered agents through `ToolRegistry`.
5. `VisionAgent` creates a caption with BLIP when available.
6. Retrieval and memory modules add previous context and style knowledge.
7. Specialist prompt agents create scene, character, layout, pose, expression, lighting, and negative sections.
8. `ContextProgramBuilder` converts agent outputs into a provider-independent context program.
9. `ContextProgramValidator` checks schema and provider compatibility.
10. `PromptAssembler` builds a canonical prompt.
11. `PromptCritic` and `LLMPromptCriticAgent` review prompt quality and semantic issues.
12. `PromptOptimizer` repairs the prompt.
13. `ProviderRouter` selects a generation provider from config.
14. `PromptCompiler` compiles Context Program into a provider-specific prompt package.
15. `ProviderPromptAdapter` converts the compiled package into final provider input.
16. `GenerationAgent` generates the image.
17. `EvaluationAgent` scores the result with CLIP when available.
18. `ReflectionAgent` and `RetryAgent` decide whether a retry is needed.
19. `MemoryManager` saves run history.
20. Debug reports and benchmark reports make the run inspectable.

## Core Features

### Planner

`PlannerAgent` produces an execution plan so the workflow is not hardcoded into one procedural script.

### LLM Intelligence Layer

`LLMContextReasoner` is a mock LLM interface for semantic planning. It does not create prompts or call an external API. It interprets user intent into user goal, scene goal, composition goal, interaction goal, style goal, and priority order.

### LLM Architecture

The shared `llm/` layer provides a provider abstraction for LLM-style reasoning, critique, and optimization.

```text
LLMContextReasoner -> LLMClient.reason()
LLMPromptCriticAgent -> LLMClient.critic()
LLMPromptOptimizerAgent -> LLMClient.optimize()
LLMClient -> AIModelService -> LLMProviderRegistry -> MockProvider
```

`LLM_PROVIDER=mock` is the default. Future provider names such as `openai`, `gemini`, `claude`, and `ollama` are recognized as integration points, but only `MockProvider` performs real local behavior now. No external LLM API is called by default.

### AI Model Layer

`AIModelService` is the shared model service boundary below `LLMClient`. Agents do not call OpenAI, Gemini, Claude, or Ollama directly. Provider skeletons live under `llm/providers/`, and all non-mock providers currently fall back to mock behavior without external API calls.

### Execution Engine

`DynamicExecutionEngine` dispatches each step and supports state-based agents through `run(state) -> dict`.

### Memory

`MemoryManager` stores run history and supports semantic-like retrieval from previous prompts, scores, reflections, retries, and output paths.

### Retrieval

Knowledge retrieval adds style and prompt context before prompt assembly.

### Context Engineering

`ContextProgramBuilder` creates a structured context program with task, user goal, scene, character, style, layout, pose, expression, lighting, negative, memory, retrieval, provider, and output sections.

`ContextProgramValidator` checks required sections, basic section types, and provider compatibility warnings before prompt assembly.

### Prompt Engineering

The workflow separates canonical prompt, provider prompt, evaluation prompt, retry prompt, and context program.

`LLMPromptCriticAgent` is an optional mock/fallback semantic critic. It does not modify prompts and does not call an external LLM API by default. It creates a structured critique report for semantic issues, conflicts, priority issues, and provider suitability.

Optional local flags:

```text
LLM_PROMPT_CRITIC_ENABLED=false
LLM_PROMPT_CRITIC_MOCK=true
LLM_PROMPT_CRITIC_PROVIDER=openai
```

Do not commit real API keys or token values.

### Provider Routing

`ProviderRouter` reads provider capability configuration from `config/providers.json`.

### Provider Adapter

`ProviderPromptAdapter` compiles the context/canonical prompt into provider-specific instructions for FLUX, GPT Image skeleton, or SDXL skeleton.

### Prompt Compiler

`PromptCompiler` converts provider-independent `context_program` into a provider-specific `compiled_prompt_package`. FLUX receives a short dense positive prompt, SDXL keeps positive and negative prompts separated, and GPT Image keeps structured prompt blocks for longer instructions.

### FastAPI

The `api/` package exposes a REST service layer with `/`, `/health`, and `/generate`.

### Gradio

The `ui/` package provides the interactive local demo interface.

### Benchmark

`benchmark/benchmark_runner.py` runs multiple prompts and stores structured result JSON.

### Debug Report

`DebugReportManager` saves `report.json`, `prompt_preview.txt`, and available output image copies under `outputs/runs/`.

## Project Structure

```text
agents/       Agent classes for planning, prompt orchestration, routing, generation flow
api/          FastAPI service layer
benchmark/    Benchmark runner, result JSON, comparison reports
config/       Provider capability configuration
docs/         Architecture, roadmap, decisions, sprint book, prompts, reviews
knowledge/    Knowledge and style retrieval resources
llm/          Shared LLM client abstraction and mock provider
memory/       MemoryManager and run history
registry/     ToolRegistry for agent/tool dispatch
tools/        BLIP, FLUX, CLIP wrappers
ui/           Gradio app
workflow/     Execution engine, AgentState, debug report, pipeline
outputs/      Runtime outputs only
```

Do not commit `.env` or the full `outputs/` directory.

## Installation

```bash
pip install -r requirements.txt
```

Create a local `.env` file:

```text
HF_TOKEN=your_local_token_here
```

Never commit real token values.

## Quick Start

Run Gradio:

```bash
python main.py
```

Run FastAPI:

```bash
uvicorn api.app:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Run Benchmark:

```bash
python -m benchmark.benchmark_runner
```

Run Report Generator:

```bash
python -m benchmark.report_generator
```

## Project Roadmap

- Sprint 1-39: Multi-agent framework, provider routing, debug reports, benchmark reports, context program
- Sprint 40: Context Program Validator
- Sprint 41: LLM Context Reasoner
- Sprint 43: LLM Prompt Critic
- Sprint 45: Prompt Compiler
- Sprint 46: AI Model Service Layer
- Sprint 41: Docker
- Sprint 42: Docker Compose
- Sprint 43: Queue
- Sprint 44: Deploy
- Sprint 45: Dashboard
- Sprint 46: Benchmark Dashboard
- Sprint 47: Multi-session
- Sprint 48: Prompt Template Library
- Sprint 49: Style Transfer
- Sprint 50: Production hardening

## Screenshots

Placeholder: curated demo screenshots should be stored under `assets/demo/` in a future sprint. Do not use the full runtime `outputs/` folder as a demo asset archive.

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

## Future Work

- Context Program v2
- Real LLM prompt optimizer
- Multi-provider generation
- Reference image handling
- Image editing workflow
- Docker/FastAPI deployment
- Benchmark dashboard

## License

TODO: Add a project license before public release.
