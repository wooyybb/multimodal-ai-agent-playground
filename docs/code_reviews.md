# Code Reviews

## Review Policy

Code review focuses on behavioral regressions, unclear boundaries, missing validation, and missing tests.

## Current Review Summary

- Agent boundaries are mostly clear.
- ExecutionEngine centralizes workflow order.
- ToolRegistry decouples execution from concrete classes.
- ContextProgramBuilder improves separation between context and prompt compilation.
- DebugReportManager improves observability.

## Known Review Risks

- Context Program schema is not yet validated.
- Provider compiler behavior needs targeted tests.
- Some fallback paths are intentionally permissive and should be hardened before production.
- Benchmark reports should not be treated as absolute image quality evaluation.

## Review Checklist

- Does the change stay inside allowed files?
- Does it preserve existing workflow compatibility?
- Does it update relevant documentation?
- Does it avoid leaking `.env` or token values?
- Does it keep runtime outputs out of curated docs?
- Does `compileall` pass?

## TODO

Add per-sprint review links when the project starts using pull requests.

## Sprint43 Review

LLMPromptCriticAgent was added as a report-only critic. It does not mutate prompts, does not call external APIs, and preserves the existing rule-based PromptCriticAgent path. The main risk is score calibration, which should be tested when a real LLM backend is connected.

## Sprint44 Review

The shared LLM client layer removes duplicated mock behavior from LLM-style agents. Current implementation keeps `MockLLM` as the only concrete provider and avoids external API calls. Future provider implementations should be tested behind the same `BaseLLM` interface.

## Sprint45 Review

PromptCompiler was added between ProviderRouter and ProviderPromptAdapter. It creates `compiled_prompt_package` without changing generation tools. ProviderPromptAdapter now prefers the compiled package and falls back to the previous canonical/context path when no package exists.

## Sprint46 Review

AIModelService was added below LLMClient. Provider skeletons do not call external APIs and currently fallback to MockProvider behavior. This keeps provider integration isolated from LLM agents.

## Sprint47 Review

OpenAIProvider now attempts real OpenAI calls only when `OPENAI_API_KEY` is available. It never logs keys, parses JSON responses defensively, and falls back to MockProvider on missing key, client failure, request failure, or parse failure.
