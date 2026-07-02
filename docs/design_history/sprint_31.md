# Sprint 31: Prompt Optimizer Agent

## Problem

PromptCriticAgent analyzes prompt issues, but its report did not improve the generation prompt.

## Decision

Add PromptOptimizerAgent to remove duplicates, repair missing sections, control length, and remove internal context before provider routing.

## Alternatives

- Keep PromptCritic results as documentation only.
- Optimize inside ProviderPromptAdapter.
- Introduce an LLM optimizer immediately.
- Use the existing prompt without repair.

## Reason

The Critic-Optimizer pattern is central to a self-improving agent workflow. A rule-based optimizer is deterministic and easier to debug before adding an LLM optimizer.

## Future Work

- LLM-based prompt optimizer
- Provider-specific optimization
- Optimization score tracking
- A/B prompt evaluation
