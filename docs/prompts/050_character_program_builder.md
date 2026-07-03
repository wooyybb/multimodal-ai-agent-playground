# Sprint 50 Prompt Archive

## Task

Create a Character Program from Vision Result and caption.

## Architecture Prompt

The target flow is `Vision -> Vision Result -> Character Program -> Scene Program -> Context Program -> Prompt Compiler`.

## Files Allowed

`agents/character_program_builder.py`, execution engine, registry, planner, debug report, README, and docs.

## Files Forbidden

Generation, evaluation, memory, FastAPI, Docker, and benchmark code were kept out of scope.

## Done Definition

The sprint is complete when Character Program is generated, injected into Context Program, available to PromptCompiler, and saved in Debug Report.
