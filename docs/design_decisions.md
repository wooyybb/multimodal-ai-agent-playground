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
