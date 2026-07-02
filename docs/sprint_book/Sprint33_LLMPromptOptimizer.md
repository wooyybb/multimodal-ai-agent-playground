# Sprint 33: LLM Prompt Optimizer Interface

## Objective

Add an optional LLM prompt optimization interface after the rule-based PromptOptimizerAgent.

## Problem

Rule-based optimization is predictable but limited for natural prompt rewriting and complex intent handling.

## Design Decision

Create `LLMPromptOptimizerAgent` with disabled, mock, and future llm modes. Keep real API calls out of this Sprint.

## Implementation Summary

- Added `agents/llm_prompt_optimizer_agent.py`.
- Added `llm_prompt_optimizer` to PlannerAgent execution plan.
- Registered the agent in OrchestratorAgent.
- Added `_run_llm_prompt_optimizer()` to DynamicExecutionEngine.
- Added README and documentation for environment flags and fallback behavior.

## AI Agent Concept

This Sprint introduces optional AI service integration and hybrid rule plus LLM optimization.

## Prompt Engineering Note

The interface reads the existing optimized prompt, critic report, sections, scene plan, provider, and routing state. Mock mode performs deterministic cleanup without calling an API.

## Interview Talking Points

- The LLM optimizer is an extension point, not a required service.
- Fallback strategy keeps the workflow stable.
- Future provider clients can be added inside `_run_llm_optimizer()`.

## Future Work

- Real OpenAI or local LLM integration
- Provider-specific prompt rewriting
- Prompt benchmark and A/B evaluation
