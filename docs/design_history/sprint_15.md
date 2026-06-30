# Sprint 15: PlannerAgent

## Problem

기존 workflow는 고정된 순서로만 실행되어 사용자 요청에 따른 작업 계획 개념이 부족했습니다.

## Decision

Rule-based PlannerAgent를 도입하여 execution plan을 생성합니다.

## Alternatives

- Fixed workflow 유지
- LLM-based planner 바로 도입
- LangGraph 기반 planner 도입

## Reason

MVP 단계에서는 rule-based planner가 디버깅하기 쉽고, Planner와 Orchestrator의 책임 분리를 학습하기에 적합합니다.

## Future Work

LLM-based planning, dynamic execution engine, tool selection, conditional workflow로 확장합니다.
