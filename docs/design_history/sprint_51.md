# Sprint 51 Design History

## Problem

PlannerAgent created an execution plan but did not explicitly represent what the generation should prioritize.

## Decision

Add `GoalPlanner` and `goal_tree`.

## Reason

Execution order and goal hierarchy are different concerns. Goal Tree keeps identity, style, composition, lighting, and background priorities available to downstream context and prompt compilation.

## Future

Connect Goal Planning to richer LLM reasoning and benchmark whether explicit priority planning improves output consistency.
