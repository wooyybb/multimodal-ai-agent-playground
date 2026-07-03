# Sprint 53 Prompt Archive

## Task

Add a Strategy Selector before Adaptive Planning.

## Architecture Prompt

The target flow is `Reflection -> Hypothesis -> Strategy Generator -> Strategy Selector -> Adaptive Planning`.

## Files Allowed

`agents/strategy_selector.py`, execution engine, tool registry, adaptive planner, debug report, README, and docs.

## Done Definition

StrategySelector runs, candidate strategies and selected strategy are stored, AdaptivePlanner uses selected strategy, PromptCompiler receives strategy context, debug report saves strategy data, and compileall succeeds.
