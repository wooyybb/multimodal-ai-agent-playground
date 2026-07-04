# Multimodal AI Agent Playground

**Context Engineering based Multi-Agent Framework for Image Generation**

![Status](https://img.shields.io/badge/status-v1.0_portfolio_ready-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)
![AI Agent](https://img.shields.io/badge/Architecture-Multi--Agent-purple)
![FastAPI](https://img.shields.io/badge/API-FastAPI-teal)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange)

Multimodal AI Agent Playground is a multimodal AI Agent framework that integrates **Vision Understanding**, **LLM Reasoning**, **Context Program**, **Prompt Compiler**, **Provider Routing**, **Generation**, **Multi-Metric Evaluation**, **Reflection**, and **Adaptive Planning** into one inspectable workflow.

It is not a simple image generation demo. It is a framework-style project that shows how an AI generation system can reason before generation, evaluate after generation, and improve through an agent loop.

## Why This Project?

Most image generation demos stop at:

```text
User Input
-> Prompt
-> Generation
-> Result
```

This project builds the full agent loop around image generation:

```text
Before Generation
-> Vision Understanding
-> Character Program
-> Goal Planning
-> LLM Context Reasoning
-> Context Program
-> Prompt Compiler
-> Provider Routing

After Generation
-> Multi-Metric Evaluation
-> Reflection
-> Self Verification
-> Strategy Selection
-> Adaptive Planning
-> Retry
-> Memory
-> Debug Report / Benchmark
```

The goal is to make every decision inspectable: what the system understood, what it prioritized, how it compiled the prompt, how it evaluated the result, and why it decided to retry or re-plan.

## Architecture

```text
User
  |
  +--> Gradio UI
  |
  +--> FastAPI
          |
          v
Vision Layer
  |
  v
LLM Reasoning Layer
  |
  v
Goal Tree / Character Program
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
Multi-Metric Evaluation
  |
  v
Reflection
  |
  v
Hypothesis / Strategy Selector
  |
  v
Self Verification
  |
  v
Adaptive Planning
  |
  v
Memory
  |
  +--> Debug Report
  |
  +--> Benchmark
```

## Core Features

| Module | Description | Status |
| --- | --- | --- |
| Multi-Agent Orchestration | Coordinates specialized agents through an orchestrator and execution engine. | Implemented |
| State-based Execution Engine | Runs workflow steps through shared state and dynamic execution. | Implemented |
| Tool Registry | Registers and invokes agents/tools by name. | Implemented |
| Multi-VLM Adapter | Keeps BLIP as default while preparing Florence/Qwen-style VLM extension. | Implemented |
| Character Program | Converts caption/vision result into structured character identity data. | Implemented |
| Context Program | Builds provider-independent structured context before prompt compilation. | Implemented |
| Context Validator | Checks context schema and provider compatibility. | Implemented |
| Goal Planner | Creates goal hierarchy, priorities, and success criteria. | Implemented |
| Prompt Compiler | Converts Context Program into provider-specific prompt packages. | Implemented |
| LLM Prompt Critic | Adds semantic prompt critique through the LLM client layer. | Implemented |
| AI Model Service | Abstracts mock/OpenAI/Gemini/Claude/Ollama-style model providers. | Implemented |
| Provider Router | Selects provider using config-driven capability rules. | Implemented |
| Multi-Metric Evaluation | Aggregates CLIP, identity, prompt, and aesthetic metrics. | Implemented |
| Reflection Loop | Produces improvement direction from evaluation results. | Implemented |
| Hypothesis Generator | Represented through reflection/adaptive planning findings. | Rule-based |
| Strategy Selector | Generates candidate strategies and chooses the best one. | Implemented |
| Self Verification | Checks goal satisfaction and replanning necessity before adaptation. | Implemented |
| Adaptive Planning | Updates context and retry strategy based on verification/strategy. | Implemented |
| Debug Report | Saves report JSON, prompt preview, trace, and output references. | Implemented |
| Benchmark Runner | Runs multiple prompts and stores comparable result JSON. | Implemented |
| FastAPI | Provides REST API and Swagger docs. | Implemented |
| Gradio | Provides local interactive demo UI. | Implemented |

## Project Structure

```text
agents/       Agent classes for planning, reasoning, prompt critique, strategy, and adaptation
workflow/     Dynamic execution engine, AgentState, debug report, and pipeline facade
tools/        BLIP, FLUX, CLIP wrappers and VLM adapter implementations
llm/          LLM client, AIModelService, provider registry, and provider skeletons
evaluation/   Metric abstraction and evaluation aggregator
memory/       MemoryManager and run history
knowledge/    Knowledge/style retrieval resources
api/          FastAPI service layer
ui/           Gradio interface
benchmark/    Benchmark runner, result files, and report generator
docs/         Architecture, roadmap, sprint book, prompts, decisions, and interview notes
outputs/      Runtime output directory; do not use as curated demo assets
```

## How to Run

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

## Environment Variables

Do not commit real keys or `.env` files.

| Variable | Purpose |
| --- | --- |
| `HF_TOKEN` | Hugging Face access token for model/provider access. |
| `OPENAI_API_KEY` | Optional key for OpenAI provider experiments. |
| `LLM_PROVIDER` | Selects LLM provider mode, such as `mock` or `openai`. |
| `VLM_PROVIDER` | Selects VLM provider mode, such as `blip`. |

## Current Limitations

- BLIP is used as the default VLM.
- FLUX is the current generation provider path.
- OpenAI, Gemini, Claude, and Ollama providers are designed as extensible service boundaries.
- CLIP-based evaluation is supplemented with rule-based identity, prompt, and aesthetic metrics.
- Image quality still depends on external model/provider behavior.
- Some advanced reasoning layers are rule-based or mock-first to keep the framework inspectable.

## Roadmap

| Release | Focus |
| --- | --- |
| v0.1 | Core Pipeline: Vision, Prompt, Generation, Evaluation, Retry |
| v0.2 | Multi-Agent Framework: Orchestrator, Registry, Execution Engine |
| v0.3 | Context Engineering: Context Program, Validator, Prompt Compiler |
| v0.4 | Intelligence Layer: Goal Planning, LLM Client, Strategy Selection, Self Verification |
| v0.5 | Evaluation & Observability: Multi-Metric Evaluation, Debug Report, Benchmark |
| v1.0 | Docker, CI, deployment guide, curated demo release |

## Portfolio Positioning

This project demonstrates:

- AI Agent Architecture
- Context Engineering
- Prompt Engineering
- Multimodal AI workflow design
- Backend API design with FastAPI
- Evaluation pipeline design
- Framework refactoring and modular system design
- Debuggability and observability for AI systems

## Documentation

- [Architecture](docs/architecture.md)
- [Project Summary](docs/project_summary.md)
- [Demo Guide](docs/demo_guide.md)
- [Interview Notes](docs/interview_notes.md)
- [Roadmap](docs/roadmap.md)

## License

TODO: Add a project license before public release.
