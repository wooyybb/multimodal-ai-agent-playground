# Sprint 33: LLM Prompt Optimizer Interface

## Problem

Rule-based PromptOptimizer is stable, but it has limits when rewriting long prompts naturally or reflecting complex intent.

## Decision

Add `LLMPromptOptimizerAgent` with disabled, mock, and future llm modes. Do not call a real external LLM API in this Sprint.

## Alternatives

- Keep only the rule-based optimizer.
- Replace PromptOptimizerAgent with an LLM implementation.
- Integrate OpenAI API immediately.
- Run LLM optimization inside ProviderPromptAdapter.

## Reason

Interface-first design validates workflow structure without requiring API keys or vendor integration. It also keeps fallback behavior explicit.

## Future Work

- OpenAI API integration
- Local LLM optimizer
- Provider-specific LLM prompt rewriting
- A/B prompt evaluation
