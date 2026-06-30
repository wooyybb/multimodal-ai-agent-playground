# Sprint 03

## Objective

단일 pipeline을 OrchestratorAgent 중심 multi-agent 구조로 확장합니다.

## Background

agent가 늘어나면 실행 순서와 결과 trace를 관리할 coordinator가 필요합니다.

## Problem

`workflow/pipeline.py`가 모든 agent를 직접 호출하면 책임이 커집니다.

## Design Decision

`OrchestratorAgent`를 추가하고 pipeline은 entry point 역할에 집중하게 했습니다.

## Architecture

```text
Pipeline -> OrchestratorAgent -> VisionAgent -> PromptAgent
```

## Implementation Summary

caption, final_prompt, agent_trace를 반환하는 구조를 만들었습니다.

## AI Agent Concept

Orchestration.

## Prompt Engineering Note

LangGraph/CrewAI 없이 Python class 기반으로 시작하도록 제약했습니다.

## Codex Usage

Codex는 기존 pipeline 책임을 Orchestrator로 이동하는 작업에 사용했습니다.

## Debugging Experience

trace가 multi-agent 흐름을 설명하는 데 중요하다는 점을 확인했습니다.

## Interview Talking Points

- 예상 질문: OrchestratorAgent는 왜 필요한가요?
- 예상 답변: 실행 순서, trace, retry, memory 연결을 중앙에서 조율하기 위해서입니다.
- 꼬리 질문: pipeline과 차이는 무엇인가요?

## Lessons Learned

Orchestrator는 agent가 아니라 workflow coordinator입니다.

## Future Work

Generation, Evaluation, Reflection을 Orchestrator에 연결합니다.
