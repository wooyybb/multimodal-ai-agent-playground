# Meeting Log

## Sprint 19: Dynamic Execution

Decision: Introduce `DynamicExecutionEngine`.

Reason: The workflow needed a central runtime instead of direct sequential calls.

## Sprint 22: Prompt Orchestration

Decision: Split prompt construction into specialist agents.

Reason: Character, style, layout, lighting, and negative prompts have different responsibilities.

## Sprint 26-28: Provider Layer

Decision: Add ProviderPromptAdapter, ProviderRouter, and provider config.

Reason: Provider selection and provider-specific prompt formatting should be extensible.

## Sprint 34: AgentState

Decision: Add shared state object.

Reason: dict state was becoming hard to manage.

## Sprint 35: FastAPI

Decision: Add API service layer while keeping Gradio.

Reason: Gradio is for demos, FastAPI is for programmatic access.

## Sprint 36-38: Observability

Decision: Add debug reports, benchmark runner, and comparison reports.

Reason: Multi-agent workflows need traceability and repeatable evaluation.

## Sprint 39: Context Program

Decision: Add provider-independent Context Program.

Reason: Context Engineering and provider prompt compilation needed a clean boundary.

## Sprint 43: LLM Prompt Critic

Decision: Add an optional mock/fallback LLM prompt critic interface.

Reason: Prompt validation needs semantic critique for conflicts, priority issues, and provider suitability without replacing the deterministic rule-based critic.

## Sprint 44: LLM Provider Abstraction

Decision: Add a shared LLM client layer.

Reason: LLMContextReasoner, LLMPromptCriticAgent, and LLMPromptOptimizerAgent should share provider selection and mock behavior instead of each owning separate logic.

## Sprint 45: Prompt Compiler

Decision: Add PromptCompiler between ProviderRouter and ProviderPromptAdapter.

Reason: Context Program should compile into provider-specific prompt packages before the adapter creates final provider inputs.

## Sprint 46: AI Model Service

Decision: Add AIModelService below LLMClient.

Reason: LLM agents should remain independent from concrete providers such as OpenAI, Gemini, Claude, and Ollama.

## Future Work

- Keep meeting notes decision-focused.
- Move sprint details to sprint book.
