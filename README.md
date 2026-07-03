# Multimodal AI Agent Playground

## Project Overview

This project is a **Multimodal AI Agent Playground** for experimenting with a multi-agent image generation framework.

It combines Planning, Retrieval, Prompt Orchestration, Provider Routing, Evaluation, Reflection, Retry, and Memory into one end-to-end workflow. The project started as a simple image-to-prompt-to-generation pipeline and has evolved into a Python class-based AI Agent Engineering playground.

Current focus:

- Build an inspectable multi-agent architecture.
- Keep each agent role small and explainable.
- Use mock or fallback behavior where needed so the workflow can still run during development.
- Separate implemented features from future extensions.

## Architecture

```text
User
-> Gradio UI
-> PlannerAgent
-> DynamicExecutionEngine
-> ToolRegistry
-> VisionAgent
-> Memory Retrieval
-> Knowledge Retrieval
-> ScenePlanningAgent
-> Character / Style / Layout / Pose / Expression / Lighting Agents
-> PromptAssembler
-> PromptCritic
-> PromptOptimizer
-> LLMPromptOptimizerAgent optional interface
-> ProviderRouter
-> ProviderPromptAdapter
-> GenerationAgent
-> EvaluationAgent
-> ReflectionAgent / RetryAgent
-> MemoryManager
```

The framework uses `ToolRegistry` and `DynamicExecutionEngine` to execute an agent plan. Several upper-layer agents now support a state-based interface:

```text
run(state: dict) -> dict
```

This makes the workflow closer to a graph-style agent system while still staying lightweight and framework-free.

## Current Features

- BLIP captioning through `VisionAgent`
- FLUX generation through `GenerationAgent`
- CLIP evaluation through `EvaluationAgent`
- RAG-style knowledge and style retrieval
- Semantic-like memory retrieval from previous runs
- Prompt compression for generation and CLIP-safe evaluation prompts
- Multi-agent prompt orchestration
- Scene, character, style, layout, pose, expression, lighting, and negative prompt agents
- PromptAssembler for canonical prompt construction
- PromptCritic for duplicate, missing-section, warning, and quality-score analysis
- PromptOptimizer for report-driven prompt repair
- Optional LLMPromptOptimizerAgent interface with disabled/mock fallback modes
- ProviderRouter with config-driven provider capability loading
- ProviderPromptAdapter for provider-specific prompt formatting
- Reflection and retry decision flow
- MemoryManager for run history
- Gradio UI

## Tech Stack

- Python
- PyTorch
- Transformers
- Gradio
- Hugging Face
- BLIP
- FLUX
- CLIP
- GitHub
- Codex

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file and set your Hugging Face token:

```text
HF_TOKEN=your_local_token_here
```

Do not commit `.env` or paste real token values into documentation.

Optional LLM Prompt Optimizer flags can be configured locally:

```text
LLM_OPTIMIZER_ENABLED=false
LLM_OPTIMIZER_MOCK=true
LLM_OPTIMIZER_PROVIDER=openai
```

The current LLM optimizer is an interface-first extension. It does not call an external LLM API by default. Disabled mode keeps the existing optimized prompt, and mock mode runs a local deterministic mock optimizer. Do not put real API keys in README or committed files.

Run the app:

```bash
python main.py
```

This launches the Gradio UI. Upload an image, enter a prompt, and run the agent workflow.

Run the FastAPI service layer:

```bash
uvicorn api.app:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

FastAPI endpoints:

```text
GET  /
GET  /health
POST /generate
```

## Project Structure

```text
agents/      Specialized AI agents and orchestration roles
tools/       Model/tool wrappers such as BLIP, FLUX, and CLIP
workflow/    DynamicExecutionEngine and pipeline logic
registry/    ToolRegistry for agent/tool lookup and execution
memory/      MemoryManager and run history storage
knowledge/   Knowledge and style retrieval resources
config/      Provider capability configuration
docs/        Architecture notes, sprint book, decisions, prompts, reviews
ui/          Gradio application
api/         FastAPI REST service layer
outputs/     Runtime generated outputs
```

`outputs/` is runtime output storage. Do not treat the whole folder as curated demo assets for Git.

## Debug Reports

Each generation run can save a debug report under:

```text
outputs/runs/run_*/report.json
outputs/runs/run_*/prompt_preview.txt
outputs/runs/run_*/initial.png
outputs/runs/run_*/retry.png
outputs/runs/run_*/best.png
```

`report.json` stores structured intermediate state such as scene plan, prompt sections, prompt critic report, optimized prompt, provider prompt, evaluation prompt, score, retry result, and agent trace.

`prompt_preview.txt` is a human-readable summary for interviews and debugging. It shows the prompt lifecycle from user request to provider prompt and evaluation result.

Runtime images are copied only when the corresponding source files exist. Do not commit the whole `outputs/` directory.

## Sprint History

- Sprint 00: Project skeleton
- Sprint 01: VisionAgent with BLIP interface
- Sprint 02: PromptAgent
- Sprint 03: OrchestratorAgent
- Sprint 04: GenerationAgent and mock/FLUX generation path
- Sprint 05: EvaluationAgent and CLIP evaluation
- Sprint 06: Reflection and Retry agents
- Sprint 07: MemoryManager
- Sprint 08: Retry loop
- Sprint 09: Gradio UI
- Sprint 10: Real BLIP integration
- Sprint 11: Real FLUX integration
- Sprint 12: Real CLIP integration
- Sprint 13: Integration validation
- Sprint 14: PlannerAgent planning phase
- Sprint 15: PlannerAgent integration
- Sprint 16: ToolRegistry
- Sprint 17: Context engineering
- Sprint 18: Prompt compression
- Sprint 19: DynamicExecutionEngine
- Sprint 20: RAG style library
- Sprint 21: Semantic-like memory retrieval
- Sprint 22: Multi-agent prompt orchestration
- Sprint 23: Character reference handling
- Sprint 24: Layout planning
- Sprint 25: Scene planning
- Sprint 26: ProviderPromptAdapter
- Sprint 27: ProviderRouter
- Sprint 28: Provider capability config
- Sprint 29: PromptCriticAgent
- Sprint 30A: Standard `run(state) -> dict` interface migration
- Sprint 31: PromptOptimizerAgent
- Sprint 32: Intelligent Prompt Optimizer
- Sprint 33: LLM Prompt Optimizer Interface
- Sprint 35: FastAPI Service Layer
- Sprint 36: Prompt Debug Report and Trace Viewer

## Roadmap

Planned future work:

- Real LLM Prompt Optimizer integration
- `AgentState` dataclass or state schema validation
- Multi-provider generation
- Reference image handling improvements
- Image editing workflow
- Docker / FastAPI deployment hardening

## Notes

Some parts of the system use real model integrations when local dependencies and credentials are configured. Fallback or mock behavior may still exist to keep the workflow runnable during development.
