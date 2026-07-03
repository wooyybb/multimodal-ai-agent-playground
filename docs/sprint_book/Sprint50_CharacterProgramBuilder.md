# Sprint 50 Character Program Builder

## Objective

Add a structured character representation between Vision Result and Context Program.

## Background

BLIP captions are useful, but character preservation needs more than one sentence. The framework needs identity, appearance, pose, expression, colors, and preservation rules as reusable context.

## Problem

A caption such as "a woman in white clothes holding a sword" does not explicitly separate gender, outfit, accessory, role, pose, or identity rules.

## Design Decision

Add `CharacterProgramBuilder` as a rule-based parser for the current sprint.

## Architecture

```text
Vision Result
-> CharacterProgramBuilder
-> Character Program
-> Context Program
-> Prompt Compiler
```

## Implementation Summary

- Added `agents/character_program_builder.py`.
- Added the step after `vision` in planner and execution engine.
- Injected character program data into context program characters.
- Added character program to debug report and prompt preview.

## AI Agent Concept

Character Program is a structured context object, not a prompt. It supports identity preservation across future provider prompts and style transfer flows.

## Prompt Engineering Note

Prompt text should be compiled from structured context rather than used as the only representation of character identity.

## Codex Usage

Codex implemented the agent, connected it through the existing registry/execution pattern, and documented the design.

## Debugging Experience

The main constraint was integrating with Context Program and Prompt Compiler without modifying their source files in this sprint.

## Interview Talking Points

- Caption is descriptive text.
- Character Program is structured identity data.
- Prompt Compiler can use the structured data to preserve character details.

## Lessons Learned

Stable multimodal workflows benefit from intermediate representations between perception and generation.

## Future Work

Add richer VLM parsing, multi-character tracking, and identity consistency metrics.
