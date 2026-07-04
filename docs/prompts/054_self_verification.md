# Sprint 54 Prompt Archive

## Task

Add SelfVerificationAgent before StrategySelector and AdaptivePlanner.

## Architecture Prompt

The target flow is `Evaluation -> Reflection -> Hypothesis -> Self Verification -> Strategy Selector -> Adaptive Planning`.

## Files Allowed

`agents/self_verification_agent.py`, planner, orchestrator, execution engine, tool registry, debug report, README, and docs.

## Done Definition

SelfVerificationAgent runs, `self_verification` is generated, StrategySelector references verification results, debug report saves verification data, and compileall succeeds.
