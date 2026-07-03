# Sprint 39: Context Program Builder

## Objective

Prompt Orchestration 결과를 바로 긴 prompt로 합치지 않고, provider-independent structured context program으로 정리하는 framework layer를 추가한다.

## Background

프로젝트는 Character, Style, Layout, Pose, Expression, Lighting, Negative Prompt Agent를 가진 multi-agent prompt orchestration 구조로 발전했습니다. Agent 수가 많아지면서 prompt assembly가 context planning까지 함께 떠안는 문제가 생겼습니다.

## Problem

Agent state와 generation prompt가 섞이면 prompt가 길어지고 provider별 formatting을 바꾸기 어렵습니다.

## Design Decision

`ContextProgramBuilder`를 추가하고, `PromptAssembler`와 `ProviderPromptAdapter`가 `context_program`을 참조하도록 변경했습니다.

## Architecture

```text
PlannerAgent
-> DynamicExecutionEngine
-> Specialist Prompt Agents
-> ContextProgramBuilder
-> PromptAssembler
-> PromptCritic / PromptOptimizer
-> ProviderRouter
-> ProviderPromptAdapter
-> GenerationAgent
```

## Implementation Summary

- Added `agents/context_program_builder.py`.
- Added `context_program_builder` to Planner and ExecutionEngine.
- Registered ContextProgramBuilder in Orchestrator.
- PromptAssembler now compiles visual content from Context Program when present.
- ProviderPromptAdapter now builds provider-specific prompts from Context Program when present.
- DebugReportManager stores context program fields in `report.json` and `prompt_preview.txt`.

## AI Agent Concept

This Sprint introduces a Context Program as a structured intermediate representation. It is similar to a prompt plan or prompt IR: the system first builds a structured understanding of the task, then compiles it into provider-specific prompts.

## Prompt Engineering Note

The main prompt pattern was:

```text
Task
-> Architecture
-> Workspace
-> Files Allowed
-> Files Forbidden
-> Requirements
-> Documentation
-> Done Definition
```

## Codex Usage

Codex was used to inspect existing orchestration flow, add a scoped agent, update execution routing, and document the design decision without modifying forbidden model, UI, memory, or API files.

## Debugging Experience

The main risk was preserving legacy prompt paths. The implementation keeps fallback behavior so PromptAssembler and ProviderPromptAdapter still work when `context_program` is absent.

## Interview Talking Points

Q. Context Program이란?
A. Prompt를 만들기 전 agent context를 구조화한 provider-independent intermediate representation입니다.

Q. 왜 prompt에 그대로 넣지 않나요?
A. Context Program에는 내부 state와 planning metadata가 포함될 수 있습니다. Generation prompt에는 visual instruction만 들어가야 합니다.

Q. ProviderAdapter와의 관계는?
A. ProviderAdapter는 Context Program을 provider별 prompt 형식으로 컴파일합니다.

## Lessons Learned

Agent가 많아질수록 prompt text보다 intermediate representation이 중요해집니다.

## Future Work

- Context Program schema validation
- Provider-specific compiler tests
- Debug/benchmark report에서 context program 비교
