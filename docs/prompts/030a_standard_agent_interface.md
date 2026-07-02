# Sprint 30A Prompt Archive

## Purpose

Standardize selected Agent interfaces toward `run(state: dict) -> dict`.

## Prompt Pattern

- Goal
- Why
- Learning Objective
- Workspace Rule
- Files Allowed
- Files Forbidden
- Interface Rule
- Backward Compatibility
- ToolRegistry update
- ExecutionEngine update
- Agent updates
- Documentation
- Done Definition

## Key Instruction

The prompt emphasized incremental refactoring. Only ScenePlanningAgent, PromptAssembler, PromptCriticAgent, ProviderRouter, and ProviderPromptAdapter were migrated in this Sprint.

## Reason

The architecture needs a simpler execution model, but the existing BLIP/FLUX/CLIP, retry, memory, and UI workflow must remain stable.
