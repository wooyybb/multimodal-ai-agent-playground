# Sprint 19: Dynamic Execution Engine

## Problem

PlannerAgent가 `execution_plan`을 생성하지만 OrchestratorAgent가 여전히 고정된 순서로 agent를 직접 실행하고 있었다. 이 구조에서는 Planner가 계획은 만들지만 실제 실행 제어권은 갖지 못한다.

## Decision

`DynamicExecutionEngine`을 추가해 `execution_plan`을 순회하면서 `ToolRegistry.call(step)` 기반으로 각 step을 실행하도록 변경했다.

## Alternatives

- 기존 고정 실행 유지
- OrchestratorAgent 내부에서 for-loop 실행
- LangGraph 도입
- LLM Planner 도입

## Reason

MVP 단계에서는 별도 ExecutionEngine class가 역할 분리와 디버깅에 가장 적합하다. Orchestrator는 planning과 coordination을 담당하고, ExecutionEngine은 step별 state transition을 담당한다.

## Future Work

- conditional branch
- parallel execution
- LLM planner
- LangGraph-style node graph
- plan validation
