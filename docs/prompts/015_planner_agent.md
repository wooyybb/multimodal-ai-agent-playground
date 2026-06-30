# Prompt 015: PlannerAgent

## Summary

이번 prompt는 fixed workflow를 PlannerAgent 기반 workflow로 확장하기 위한 Sprint 15 Architecture Prompt입니다.

## Purpose

`PlannerAgent`가 user prompt와 image 제공 여부를 기반으로 execution plan을 생성하고, Orchestrator가 기존 workflow를 실행하면서 planner result를 기록하게 합니다.

## Key Constraints

- PlannerAgent는 계획만 생성합니다.
- OrchestratorAgent는 계획을 기록하고 기존 workflow를 실행합니다.
- 이번 Sprint에서는 dynamic execution engine을 구현하지 않습니다.
- tools, UI, requirements, memory는 수정하지 않습니다.

## Done Definition

- `python -m compileall agents tools workflow memory ui` 성공
- `PlannerAgent` execution plan 반환
- result dict에서 `planner_result` 확인 가능
- 기존 E2E workflow 유지
- Documentation 업데이트 완료
- Workspace 밖 파일 생성 없음
