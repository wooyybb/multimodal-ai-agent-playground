# Sprint29 Prompt Critic Agent

## Objective

Add a `PromptCriticAgent` that reviews the canonical prompt before provider routing and generation.

## Background

The project already builds structured prompts through PromptAssembler, but the prompt moved directly into provider routing without a quality check.

## Problem

Duplicated quality tags, missing layout details, unclear character interaction, and prompt length issues can reduce generation quality.

## Design Decision

Insert `PromptCriticAgent` after `PromptAssembler` and before `ProviderRouter`.

## Architecture

```text
PromptAssembler
-> PromptCriticAgent
-> ProviderRouter
-> ProviderPromptAdapter
-> GenerationAgent
```

## Implementation Summary

- Added `agents/prompt_critic_agent.py`.
- Added `prompt_critic` to the Planner execution plan.
- Registered PromptCriticAgent in OrchestratorAgent.
- Added `_run_prompt_critic` in DynamicExecutionEngine.
- Stored `prompt_report` and `prompt_quality_score` in state.

## AI Agent Concept

This Sprint introduces Self Critique and Prompt Diagnostics as an intermediate agent responsibility.

## Prompt Engineering Note

The Sprint prompt clearly separated target architecture, allowed files, forbidden files, interface, scoring rules, and done definition.

## Codex Usage

Codex was used to implement the agent, connect it to the workflow, and update architecture documentation without modifying forbidden files.

## Debugging Experience

The critic is defensive: if critique fails, the workflow keeps running with `quality_score=100` and `prompt_report=None`.

## Interview Talking Points

- PromptCriticAgent validates prompt quality before generation.
- It is separate from PromptAssembler to separate building from reviewing.
- Current critique is rule-based and can evolve into an LLM critic.

## Lessons Learned

Prompt quality should be observable before model execution, not inferred only from generated image quality.

## Future Work

- LLM-based semantic critic
- Provider-specific critic
- Automatic prompt revision loop
