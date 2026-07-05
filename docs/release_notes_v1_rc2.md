# v1.0 RC2 Release Notes

## Focus

Framework Simplification and Responsibility Refactoring.

## What Changed

- Architecture explanation simplified from agent-heavy descriptions to five responsibility layers.
- README updated so the framework can be understood quickly from the landing page.
- Architecture documentation now uses Planning, Context, Generation, Evaluation, and Infrastructure layers.
- Evaluation Layer now includes adaptive planning, strategy, hypothesis, and retry as internal evaluation-loop processes.
- ToolRegistry layer metadata updated to the five-layer responsibility model.
- ExecutionEngine logs now include layer names while preserving the existing execution flow.

## What Did Not Change

- No new agents.
- No new tools.
- No new prompts.
- No new LLM or VLM integration.
- No new evaluation metric.
- Core workflow and existing behavior are preserved.

## Next

- ExecutionEngine cleanup.
- AgentState layer ownership cleanup.
- Demo polish.
- CI and Docker smoke tests.
