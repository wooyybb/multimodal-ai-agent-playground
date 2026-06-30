# Sprint 14

## Objective

PlannerAgent를 통해 fixed workflow 위에 planning layer를 추가합니다.

## Background

실제 agentic workflow는 사용자 요청을 보고 필요한 단계와 순서를 계획해야 합니다.

## Problem

기존 workflow는 고정 순서로만 실행되어 task decomposition 개념이 약했습니다.

## Design Decision

Planned Sprint에서는 rule-based PlannerAgent부터 시작합니다. Planner는 실행하지 않고 계획만 만들며, Orchestrator가 실행을 담당합니다.

## Architecture

```text
OrchestratorAgent -> PlannerAgent -> Execution Plan -> Existing Workflow
```

## Implementation Summary

Planned: `run(user_prompt, image_provided)`가 task_type, execution_plan, reason을 반환합니다.

## AI Agent Concept

Planning Agent and Execution Plan.

## Prompt Engineering Note

Planner와 Orchestrator 책임 분리를 강하게 명시해야 합니다.

## Codex Usage

Planned: Codex는 architecture-changing task를 작은 단계로 제한하는 데 사용합니다.

## Debugging Experience

Planned: dynamic execution engine은 별도 Sprint에서 검증합니다.

## Interview Talking Points

- 예상 질문: PlannerAgent는 왜 필요한가요?
- 예상 답변: 사용자 요청에 맞는 execution plan을 생성하기 위해서입니다.
- 꼬리 질문: 현재 Planner는 LLM인가요?

## Lessons Learned

Planning과 execution은 분리해야 안전하게 확장할 수 있습니다.

## Future Work

LLM-based planning, tool selection, conditional workflow로 확장합니다.
