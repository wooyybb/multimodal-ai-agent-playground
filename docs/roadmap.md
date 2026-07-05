# Roadmap

## Release Roadmap

| Release | Goal | Status |
| --- | --- | --- |
| v0.1 | Core Pipeline: Vision, Prompt, Generation, Evaluation, Retry | Complete |
| v0.2 | Multi-Agent Framework: Orchestrator, Tool Registry, Execution Engine | Complete |
| v0.3 | Context Engineering: Context Program, Validator, Prompt Compiler | Complete |
| v0.4 | Intelligence Layer: Goal Planning, LLM Layer, Strategy Selection, Self Verification | Complete |
| v0.5 | Evaluation & Observability: Multi-Metric Evaluation, Debug Report, Benchmark | Complete |
| v1.0 RC1 | Layer-based architecture cleanup and portfolio documentation | Complete |
| v1.0 RC2 | Responsibility refactoring and framework simplification | Complete |
| v1.0 | CI, demo polish, deployment-ready release | Planned |
| v1.1 | Vision Layer upgrade with Florence2 adapter and standard vision schema | Complete |
| v1.2 | Real LLM Reasoning Layer with OpenAI provider and rule fallback | Complete |

## Completed Sprints

- Sprint 01: VisionAgent and BLIP captioning interface
- Sprint 02: PromptAgent
- Sprint 03: OrchestratorAgent
- Sprint 04: GenerationAgent and mock/FLUX generation path
- Sprint 05: EvaluationAgent and mock/CLIP evaluation path
- Sprint 06: Reflection and Retry agents
- Sprint 07: MemoryManager
- Sprint 08: One-step retry loop
- Sprint 09: Gradio UI
- Sprint 10: Real BLIP integration
- Sprint 11: Real FLUX integration with fallback
- Sprint 12: Real CLIP evaluation
- Sprint 13: Integration validation
- Sprint 14: PlannerAgent planned design
- Sprint 15: PlannerAgent integration
- Sprint 16: ToolRegistry
- Sprint 17: Context Engineering
- Sprint 18: Prompt compression and budget management
- Sprint 19: DynamicExecutionEngine
- Sprint 20: Knowledge Manager and RetrievalAgent
- Sprint 21: Semantic-like Memory Retrieval
- Sprint 22: Multi-agent Prompt Orchestration
- Sprint 23: Character Reference Handling
- Sprint 24: Layout Planning
- Sprint 25: Scene Planning
- Sprint 26: ProviderPromptAdapter
- Sprint 27: ProviderRouter
- Sprint 28: Provider capability config
- Sprint 29: PromptCriticAgent
- Sprint 30A: Standard `run(state) -> dict` agent interface
- Sprint 31: PromptOptimizerAgent
- Sprint 32: Intelligent Prompt Optimizer
- Sprint 33: LLMPromptOptimizer interface
- Sprint 34: AgentState Framework Core
- Sprint 35: FastAPI Service Layer
- Sprint 36: Prompt Debug Report and Trace Viewer
- Sprint 37: Benchmark Runner
- Sprint 38: Run Comparison Report
- Sprint 39: ContextProgramBuilder
- Sprint 39.5: Documentation Refactoring
- Sprint 40: Context Program Validator
- Sprint 41: LLM Context Reasoner
- Sprint 43: LLM Prompt Critic
- Sprint 44: LLM Provider Abstraction Layer
- Sprint 45: Prompt Compiler
- Sprint 46: AI Model Service Layer
- Sprint 47: Real OpenAI Provider Integration
- Sprint 48: Multi-VLM Adapter
- Sprint 49: Adaptive Planning Loop
- Sprint 50: Character Program Builder
- Sprint 51: Goal-oriented Planning
- Sprint 53: Strategy Selector
- Sprint 54: Self Verification
- Sprint 55: Multi-Metric Evaluation Layer
- Sprint 56: v1.0 README and GitHub polish
- Sprint 57: Docker and Docker Compose
- Sprint 58: Reference Image Parser
- Sprint 59: Real VLM Upgrade Preparation
- Sprint 60: Real LLM Reasoning Layer
- Release Candidate 1: Layer-based framework organization
- Release Candidate 2: Framework simplification and responsibility refactoring
- Version 1.1: Vision Layer Upgrade with Florence2 adapter, BLIP fallback, and structured vision result schema
- Version 1.2: Real LLM Reasoning Layer with OpenAI provider, structured JSON parsing, and rule/mock fallback

## Planned Sprints

- Sprint 61: ExecutionEngine cleanup
- Sprint 62: AgentState layer organization
- Sprint 63: CI validation and Docker smoke tests
- Sprint 64: Queue-based generation jobs
- Sprint 65: Deployment dashboard

## Future Work

- Add Context Program v2 schema enforcement.
- Add provider compiler regression tests.
- Add CI checks for Docker build and FastAPI health.
- Add persistent multi-session memory.
- Add benchmark dashboard for visual comparison.
