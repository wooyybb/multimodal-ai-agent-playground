# Sprint 53 Design History

## Problem

AdaptivePlanner produced one strategy directly, so there was no explainable comparison between alternatives.

## Decision

Add `StrategySelector` before AdaptivePlanner.

## Reason

Candidate generation and selection make the reasoning loop easier to inspect. The selected strategy becomes explicit state that downstream planning can use.

## Future

Add learned or LLM-assisted strategy scoring and compare strategy outcomes in benchmarks.
