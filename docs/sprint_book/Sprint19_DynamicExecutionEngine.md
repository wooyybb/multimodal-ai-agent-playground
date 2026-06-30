# Sprint 19: Dynamic Execution Engine

## Objective

PlannerAgent가 만든 `execution_plan`을 실제 runtime workflow에 반영한다.

## Problem

PlannerAgent는 plan을 만들고 있었지만 OrchestratorAgent가 고정된 순서로 agent를 직접 호출하고 있었다.

## Design Decision

`workflow/execution_engine.py`에 `DynamicExecutionEngine`을 추가하고, OrchestratorAgent는 초기 state를 만든 뒤 engine에 실행을 위임한다.

## Implementation Summary

- `DynamicExecutionEngine.run(execution_plan, registry, state)` 구현
- `memory_load`, `vision`, `prompt_compressor`, `prompt`, `generation`, `evaluation`, `reflection`, `retry`, `memory_save` step 지원
- PlannerAgent 기본 plan에 `prompt_compressor` 추가
- OrchestratorAgent 직접 step 실행 로직 제거
- 기존 UI 반환 key 유지

## AI Agent Concept

Dynamic Execution Engine은 plan을 runtime dispatch로 바꾸는 계층이다. Planner는 무엇을 할지 정하고, Engine은 state를 갱신하며 실제 tool을 호출한다.

## Prompt Engineering Note

이번 Sprint prompt는 state schema와 step behavior를 명시해 architecture refactoring 중 기능 회귀를 줄이도록 설계되었다.

## Interview Talking Points

Q. Dynamic Execution Engine은 왜 필요한가요?
A. Planner가 만든 plan을 실제 실행 흐름에 반영하기 위해 필요합니다.

Q. PlannerAgent와 ExecutionEngine의 차이는 무엇인가요?
A. PlannerAgent는 실행 계획을 만들고, ExecutionEngine은 그 계획을 state와 registry를 통해 실행합니다.

Q. state dict는 어떤 역할을 하나요?
A. 각 step의 입력과 출력을 공유하는 runtime memory 역할을 합니다.

## Future Work

- conditional branch
- parallel execution
- dynamic plan validation
- RAG Style Library
