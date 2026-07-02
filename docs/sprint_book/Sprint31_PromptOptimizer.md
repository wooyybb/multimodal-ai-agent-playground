# Sprint 31: Prompt Optimizer Agent

## Objective

Use PromptCriticAgent reports to repair the canonical prompt before provider routing and generation.

## Problem

Prompt quality issues were visible, but not reflected in the prompt passed to the provider adapter.

## Design Decision

Add `PromptOptimizerAgent` after PromptCriticAgent and before ProviderRouter.

## Implementation Summary

- Added `agents/prompt_optimizer_agent.py`.
- Added `prompt_optimizer` to PlannerAgent execution plan.
- Registered PromptOptimizerAgent in OrchestratorAgent.
- Added `_run_prompt_optimizer()` in DynamicExecutionEngine.
- Updated ProviderPromptAdapter notes when optimized prompt is used.

## AI Agent Concept

This Sprint implements the Critic-Optimizer pattern and a rule-based prompt refinement loop.

## Prompt Engineering Note

The optimizer removes duplicated phrases, internal context terms, repairs missing sections, and controls length before provider-specific adaptation.

## Interview Talking Points

- PromptCritic diagnoses prompt quality.
- PromptOptimizer repairs the prompt.
- The optimizer is rule-based first for debugging and stability.
- Future versions can use LLM rewriting.

## Future Work

- LLM Prompt Optimizer
- Provider-specific optimizer
- A/B prompt evaluation
- Optimization score tracking
