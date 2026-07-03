# Sprint 49 Prompt Archive

## Task

Add an Adaptive Planning Loop before retry.

## Architecture Prompt

The prompt moved the flow from `Generation -> Evaluation -> Reflection -> Retry` to `Generation -> Evaluation -> Reflection -> Adaptive Planner -> Context Update -> Prompt Compiler -> Generation`.

## Files Allowed

`agents/adaptive_planner.py`, execution engine, registry, planner, debug report, README, and docs.

## Files Forbidden

Generation, evaluation, memory, UI, FastAPI, Docker, and benchmark code were kept out of scope.

## Done Definition

The sprint is complete when AdaptivePlanner runs, creates `adaptive_plan`, context updates are reflected before retry prompt compilation, debug report stores the plan, and compileall succeeds.
