# Sprint 49 Adaptive Planning Loop

## Objective

Add a re-planning step between reflection and retry.

## Background

The previous retry flow used score threshold only. That was useful as a control policy, but it did not explain what should change before the second generation attempt.

## Problem

Retry without planning can repeat the same prompt weaknesses.

## Design Decision

Introduce `AdaptivePlanner` as a rule-based agent that reads score, reflection, caption, and prompt state, then returns an `adaptive_plan`.

## Architecture

```text
Generation
-> Evaluation
-> Reflection
-> AdaptivePlanner
-> Context Update
-> PromptCompiler
-> ProviderPromptAdapter
-> Retry Generation
```

## Implementation Summary

- Added `agents/adaptive_planner.py`.
- Added `adaptive_planner` to the planner execution plan and registry defaults.
- ExecutionEngine applies adaptive context updates and re-runs prompt compiler/provider adapter before retry.
- Debug reports include `adaptive_plan`.

## AI Agent Concept

This sprint turns retry into self-improving re-planning. The agent creates a hypothesis and modifies context before acting again.

## Prompt Engineering Note

The sprint prompt emphasized failure analysis, hypothesis generation, context updates, priority changes, and no LLM usage.

## Codex Usage

Codex implemented the loop, kept forbidden areas untouched, and updated docs for interview explanation.

## Debugging Experience

The main challenge was applying context updates without changing generation or evaluation agents.

## Interview Talking Points

- Retry decides whether to try again.
- Adaptive Planning decides what to change.
- Reflection explains; AdaptivePlanner converts explanation into context updates.

## Lessons Learned

Agent loops become more useful when failure analysis is transformed into state changes before the next action.

## Future Work

Add LLM-assisted adaptive planning and benchmark score deltas between naive retry and adaptive retry.
