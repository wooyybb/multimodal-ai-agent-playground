# Sprint 17: Context Engineering

## Problem

PromptAgent가 caption과 user_prompt만 사용하여 Planner와 Memory 정보를 활용하지 못했습니다.

## Decision

OrchestratorAgent가 planner_result와 last_run을 기반으로 context dict를 구성하고, PromptAgent가 이를 선택적으로 사용하도록 확장합니다.

## Alternatives

- PromptAgent가 직접 MemoryManager 호출
- PlannerAgent가 prompt까지 생성
- RAG를 먼저 도입
- 기존 caption + user_prompt 유지

## Reason

역할 분리를 유지하면서도 prompt 품질을 높이기 위해 Orchestrator 중심 context composition이 가장 적합합니다.

## Future Work

RAG Style Library, Semantic Memory, Prompt Template Selection, LLM-based Prompt Builder로 확장합니다.
