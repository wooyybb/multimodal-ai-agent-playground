# Sprint 32: Intelligent Prompt Optimizer

## Objective

Upgrade PromptOptimizerAgent so it interprets PromptCriticAgent reports and applies only necessary edits.

## Problem

The previous optimizer performed broad rule-based cleanup and did not fully use the structure of `prompt_report`.

## Design Decision

Make optimization report-driven. The optimizer now reads duplicates, missing sections, warnings, and quality score before editing.

## Implementation Summary

- Added reasoning logs to PromptOptimizerAgent.
- Added `reasoning_steps`, `before_score`, and `after_estimated_score`.
- Added score-band behavior: high score means minimal edits, medium score means targeted repairs, low score means quality reinforcement.
- Added Prompt Preview before generation in ExecutionEngine.

## AI Agent Concept

This Sprint strengthens the Critic to Optimizer feedback loop and makes prompt editing explainable.

## Prompt Engineering Note

The optimizer is instructed to repair only what the critic report identifies, avoiding unnecessary prompt churn.

## Interview Talking Points

- The optimizer edits based on Critic Report.
- Prompt editing is explainable through reasoning steps.
- Prompt Preview helps inspect generation input before model execution.

## Future Work

- LLM Optimizer
- Provider-specific optimization
- A/B prompt evaluation
