# Sprint 31 Prompt Archive

## Purpose

Add PromptOptimizerAgent so PromptCriticAgent output can improve the canonical prompt before generation.

## Prompt Pattern

- Goal
- Learning Objective
- Why
- Workspace Rule
- Files Allowed
- Files Forbidden
- Agent Interface
- Optimization Rules
- Planner / Orchestrator / ExecutionEngine changes
- Documentation
- Done Definition

## Key Instruction

The prompt required a rule-based optimizer that updates `optimized_prompt`, `canonical_prompt`, and `final_prompt`.

## Reason

Critique without repair does not create a self-improving workflow. The optimizer closes that loop while keeping behavior deterministic.
