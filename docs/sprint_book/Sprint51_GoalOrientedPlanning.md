# Sprint 51 Goal-oriented Planning

## Objective

Add a Goal Tree before execution planning.

## Background

The planner already selected which agents should run. It did not yet encode which visual objectives should be preserved most strongly.

## Problem

Execution plan alone cannot express that identity should outweigh style, or that portrait requests should prioritize face clarity.

## Design Decision

Add `GoalPlanner` as a rule-based planning agent.

## Architecture

```text
User Prompt
-> GoalPlanner
-> Goal Tree
-> PlannerAgent
-> Execution Plan
-> Context Program
-> Prompt Compiler
```

## Implementation Summary

- Added `agents/goal_planner.py`.
- Added `goal_planner` to ToolRegistry and PlannerAgent execution plan.
- ExecutionEngine stores Goal Tree and injects priorities into Context Program.
- Debug reports include `goal_tree`.

## AI Agent Concept

Goal-oriented planning separates task execution order from task importance.

## Prompt Engineering Note

Goal Tree is not a prompt. It is a planning object used to guide later prompt compilation.

## Codex Usage

Codex implemented the agent, connected it through existing registry/execution patterns, and documented the design.

## Debugging Experience

The main constraint was reflecting priorities in PromptCompiler without editing PromptCompiler directly.

## Interview Talking Points

- Execution plan says what to run.
- Goal Tree says what to preserve.
- Adaptive Planning is after failure; Goal Planning is before generation.

## Lessons Learned

Agent systems need explicit priorities, not only ordered steps.

## Future Work

Use LLM reasoning to build richer goal hierarchies and compare goal-guided prompts in benchmarks.
