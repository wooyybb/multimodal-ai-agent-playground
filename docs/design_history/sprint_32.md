# Sprint 32: Intelligent Prompt Optimizer

## Problem

Optimizer did not use PromptReport deeply enough. It cleaned prompts broadly instead of reasoning from the critic output.

## Decision

Add PromptReport-based reasoning to PromptOptimizerAgent.

## Reason

Self-improving agents need feedback loops where critique directly controls the next action. Report-driven optimization makes edits more explainable and less destructive.

## Alternatives

- Keep the broad rule-based optimizer.
- Move optimization into ProviderPromptAdapter.
- Use an LLM optimizer immediately.

## Future

- LLM Optimizer
- Provider-specific Optimizer
- Optimization quality tracking
