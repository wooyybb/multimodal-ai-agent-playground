# Sprint 43: LLM Prompt Critic

## Problem

Rule-based PromptCritic can detect duplicate keywords, missing sections, and length problems, but it cannot fully judge scene/layout/style conflicts or provider suitability issues.

## Decision

Add `LLMPromptCriticAgent` to create a structured report for semantic issues, conflicts, priority issues, and provider suitability issues.

## Alternatives

- Use only the existing PromptCritic.
- Handle semantic issues directly inside PromptOptimizer.
- Connect a real OpenAI API immediately.
- Replace the rule-based critic with an LLM critic.

## Reason

The LLM critic should diagnose prompt problems without directly editing the prompt. This preserves the Critic-Optimizer pattern. Starting with mock/fallback behavior validates the architecture without external LLM dependencies.

## Future Work

OpenAI/local LLM critic integration, provider-specific critic rules, critic score calibration, and prompt A/B testing.
