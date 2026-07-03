# Sprint 53 Strategy Selector

## Objective

Add candidate strategy generation and selection before Adaptive Planning.

## Background

Adaptive Planning previously generated one strategy directly from reflection signals.

## Problem

Without candidates, the system could not explain why one recovery strategy was better than another.

## Design Decision

Add `StrategySelector` as a rule-based decision agent.

## Architecture

```text
Reflection
-> Hypothesis
-> StrategySelector
-> Selected Strategy
-> AdaptivePlanner
```

## Implementation Summary

- Added `agents/strategy_selector.py`.
- ToolRegistry registers StrategySelector.
- ExecutionEngine inserts `strategy_selector` before `adaptive_planner` when missing.
- AdaptivePlanner reads `selected_strategy`.
- Debug reports include candidate and selected strategy data.

## AI Agent Concept

This sprint separates candidate generation from adaptive planning, making the decision loop more explainable.

## Prompt Engineering Note

Strategy is not prompt text. It is planning state used to guide context updates before prompt compilation.

## Codex Usage

Codex implemented the selector, connected state flow, and updated documentation.

## Debugging Experience

The key integration point was adding strategy context without editing generation, evaluation, memory, UI, API, benchmark, or LLM layers.

## Interview Talking Points

- Hypothesis explains the likely failure.
- Candidate strategies represent possible fixes.
- Selected strategy guides AdaptivePlanner.

## Lessons Learned

Agent loops become more explainable when decision candidates are explicit state.

## Future Work

Add benchmark-based strategy scoring and LLM-assisted strategy generation.
