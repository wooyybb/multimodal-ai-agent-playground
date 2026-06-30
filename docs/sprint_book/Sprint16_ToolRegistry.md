# Sprint 16: Tool Registry & Tool Calling

## Objective

OrchestratorAgent와 각 Agent 호출 사이에 ToolRegistry를 도입합니다.

## Problem

OrchestratorAgent가 각 Agent를 직접 호출하여 Agent/Tool 수가 늘어날수록 결합도가 높아지는 문제가 있었습니다.

## Design Decision

Python class 기반 `ToolRegistry`를 만들고 `memory_load`, `vision`, `prompt`, `generation`, `evaluation`, `reflection`, `retry`, `memory_save`를 등록했습니다.

## Implementation Summary

`ToolRegistry.register()`와 `ToolRegistry.call()`을 구현하고, Orchestrator의 기존 workflow step 호출을 registry 기반 호출로 감쌌습니다.

## AI Agent Concept

Tool Calling, Tool Registry Pattern, Loose Coupling, Dependency Inversion.

## Prompt Engineering Note

이번 Sprint prompt는 dynamic execution engine까지 구현하지 않도록 제한하고, registry 기반 호출 구조만 도입하도록 범위를 좁혔습니다.

## Interview Talking Points

- 예상 질문: ToolRegistry는 왜 필요한가요?
- 예상 답변: Orchestrator가 모든 Agent 구현을 직접 알지 않도록 호출 계층을 분리하기 위해서입니다.
- 꼬리 질문: MCP나 tool calling과 어떤 관련이 있나요?

## Future Work

Execution plan 기반 dynamic execution, LLM-based tool selection, MCP integration으로 확장합니다.
