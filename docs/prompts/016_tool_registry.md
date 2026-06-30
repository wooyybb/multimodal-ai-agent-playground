# Prompt 016: Tool Registry & Tool Calling

## Summary

이번 prompt는 OrchestratorAgent와 Agent/Tool 호출 사이에 ToolRegistry를 도입하기 위한 Sprint 16 Architecture Prompt입니다.

## Purpose

Orchestrator가 모든 Agent 구현을 직접 호출하는 구조에서 벗어나, registry 기반 name-to-callable 호출 구조로 확장합니다.

## Key Constraints

- PlannerAgent는 execution plan만 생성합니다.
- ToolRegistry가 Agent/Tool 호출을 관리합니다.
- 이번 Sprint에서는 완전한 dynamic execution engine을 구현하지 않습니다.
- 기존 E2E workflow를 유지합니다.
- tools, UI, memory, requirements는 수정하지 않습니다.

## Done Definition

- `python -m compileall agents tools workflow memory ui registry` 성공
- 기존 E2E workflow 유지
- PlannerAgent execution_plan 유지
- ToolRegistry call 로그 출력
- agent_trace에 ToolRegistry 호출 기록 포함
- Documentation 업데이트 완료
- Workspace 밖 파일 생성 없음
