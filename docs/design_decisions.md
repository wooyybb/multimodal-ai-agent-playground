# Design Decisions

## ExecutionEngine

Decision: Add `DynamicExecutionEngine`.

Reason: Workflow order should not live as one long procedural method. A dynamic engine can execute planner output and make agent steps easier to inspect.

Future: Conditional branching, queue execution, async jobs.

## ToolRegistry

Decision: Route agent calls through `ToolRegistry`.

Reason: ExecutionEngine should call named tools/agents without importing every class directly.

Future: Capability-based tool discovery.

## AgentState

Decision: Introduce `AgentState`.

Reason: Shared dict state became large and typo-prone.

Future: Stronger validation and schema-driven state contracts.

## Context Program

Decision: Add `ContextProgramBuilder`.

Reason: Context Engineering and Prompt Engineering needed a clean boundary. Context Program is a provider-independent intermediate representation.

Future: Context Program v2 schema and provider compiler tests.

## Context Program Validation

Decision: Add `ContextProgramValidator` after `ContextProgramBuilder`.

Reason: Structured context should be checked before prompt assembly and generation. Missing sections, type mismatches, and provider compatibility warnings are easier to debug before they become prompt or generation failures.

Future: Replace rule-based checks with formal schema validation and provider-specific compiler tests.

## LLM Context Reasoner

Decision: Add `LLMContextReasoner` as a mock semantic planning layer before prompt construction.

Reason: LLM reasoning is useful for interpreting user intent, but direct prompt generation can blur the boundary between semantic planning and provider prompt compilation. Keeping the LLM layer as structured reasoning makes the system easier to inspect and replace.

Future: Connect a real LLM API behind the same interface and keep rule-based fallback behavior.

## LLM Prompt Critic

Decision: Add `LLMPromptCriticAgent` after rule-based `PromptCriticAgent` and before prompt optimization.

Reason: Rule-based checks catch duplicates, missing sections, and length problems. Semantic issues such as scene/style conflict, priority mismatch, and provider suitability need a separate critic report before optimization. The critic does not modify prompts directly.

Future: Connect OpenAI or local LLM behind the same interface, calibrate critic scores, and add provider-specific critic tests.

## LLM Provider Abstraction

Decision: Add `LLMClient`, `BaseLLM`, `MockLLM`, and `LLMProviderRegistry`.

Reason: LLMContextReasoner, LLMPromptCriticAgent, and LLMPromptOptimizerAgent should depend on a shared LLM interface rather than each owning provider/mock logic.

Future: Add OpenAI, Gemini, Claude, and Ollama implementations behind the same client interface.

## Prompt Compiler

Decision: Add `PromptCompiler` between ProviderRouter and ProviderPromptAdapter.

Reason: Context Program is provider-independent, while generation providers need different prompt package shapes. Separating compilation from adapter formatting keeps provider rules easier to test.

Future: Add provider-specific compiler tests and prompt template library support.

## AI Model Service

Decision: Add `AIModelService` below `LLMClient`.

Reason: LLM agents should not know concrete model providers. `AIModelService` owns the service boundary, while Provider Registry maps provider names to provider implementations.

Future: Add real OpenAI, Gemini, Claude, and Ollama providers behind the same interface.

## OpenAI Provider Integration

Decision: Implement OpenAIProvider behind AIModelService.

Reason: Real provider calls should be isolated from agents. This keeps LLMContextReasoner, LLMPromptCriticAgent, and LLMPromptOptimizerAgent dependent only on LLMClient.

Future: Add response schema tests, retry/backoff, and provider-specific calibration.

## VLM Adapter

Decision: Add `VLMRouter` and provider classes under `tools/vlm/`.

Reason: VisionAgent should not be permanently coupled to BLIP. A VLM adapter keeps the existing BLIP workflow stable while creating a clear extension point for Florence-2, Qwen-VL, and future multimodal models.

Future: Replace skeleton providers with real Florence/Qwen integrations and add richer object, style, and character parsing.

## Provider Adapter

Decision: Separate `ProviderRouter` and `ProviderPromptAdapter`.

Reason: Provider selection and provider prompt formatting are different responsibilities.

Future: More providers and provider-specific optimization rules.

## Debug Report

Decision: Save `report.json` and `prompt_preview.txt`.

Reason: Agent workflows need observability. JSON supports machine analysis, while preview text supports interviews and debugging.

Future: Trace viewer and dashboard.

## FastAPI

Decision: Add FastAPI as a service layer while keeping Gradio.

Reason: Gradio is useful for demos; FastAPI is useful for external programs and deployment.

Future: Auth, queue, async jobs, deployment guide.

## Benchmark

Decision: Add benchmark runner and report generator.

Reason: Single demos are not enough to evaluate an agent framework. Multiple prompts need comparable metrics and debug paths.

Future: Benchmark dashboard and curated prompt suites.

## Future Work

- Keep decisions short and architecture-level.
- Move detailed sprint notes to `docs/sprint_book/`.
