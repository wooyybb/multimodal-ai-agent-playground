# Sprint 43: LLM Prompt Critic

## Objective

Add an LLM-style prompt critique interface without replacing the existing rule-based PromptCriticAgent.

## Problem

Rule-based checks catch duplicate keywords, missing sections, and prompt length. They are weaker at semantic conflicts such as photobooth versus battle scene, style priority issues, or provider suitability.

## Design Decision

Place `LLMPromptCriticAgent` after `PromptCriticAgent` and before `PromptOptimizerAgent`. The critic creates a structured report but does not modify the prompt.

## Implementation Summary

- Added `agents/llm_prompt_critic_agent.py`.
- Added `llm_prompt_critic` to planner execution plan.
- Registered the critic in Orchestrator.
- Added ExecutionEngine support for state-based execution.
- Added debug report and prompt preview fields.
- Updated README and architecture documentation.

## AI Agent Concept

This Sprint strengthens the Critic-Optimizer pattern. The critic diagnoses semantic problems, while optimizer agents remain responsible for prompt mutation.

## Prompt Engineering Note

Prompt critique is split into deterministic rule-based critique and semantic mock/future LLM critique.

## Interview Talking Points

Q. Why not edit the prompt directly?
A. Separating critic and optimizer responsibilities keeps the workflow explainable and debuggable.

Q. Why mock first?
A. The interface and state flow should be validated before adding API cost, latency, credentials, or failure modes.

Q. Why keep rule-based critic?
A. Deterministic checks are stable and cheap. LLM critique complements them rather than replacing them.

## Future Work

- Real OpenAI/local LLM critic backend
- Provider-specific semantic critic
- Critic score calibration
- Prompt A/B testing
