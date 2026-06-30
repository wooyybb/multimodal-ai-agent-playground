# Sprint 16: Tool Registry & Tool Calling

## Problem

OrchestratorAgent가 각 Agent를 직접 호출하여 구조가 강하게 결합되어 있었습니다.

## Decision

ToolRegistry를 도입하여 Agent/Tool 호출을 중앙에서 관리합니다.

## Alternatives

- 기존 직접 호출 유지
- LangGraph 도입
- MCP 스타일 외부 Tool 서버 도입
- 완전한 dynamic execution engine 구현

## Reason

현재 MVP 단계에서는 Python class 기반 ToolRegistry가 가장 단순하고 디버깅하기 쉽습니다.

## Future Work

Dynamic execution engine, LLM-based tool selection, MCP integration, plugin architecture로 확장합니다.
