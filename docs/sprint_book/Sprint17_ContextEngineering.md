# Sprint 17: Context Engineering

## Objective

PromptAgent를 context-aware prompt builder로 확장합니다.

## Problem

PromptAgent가 caption과 user_prompt만 사용하여 Planner와 Memory 정보를 활용하지 못했습니다.

## Design Decision

OrchestratorAgent가 planner_result와 last_run을 기반으로 context dict를 구성하고, PromptAgent는 선택적으로 context를 사용합니다.

## Implementation Summary

`PromptAgent.run(caption, user_prompt, context=None)`으로 interface를 확장하고, previous best prompt와 score를 제한적으로 final prompt에 반영했습니다.

## AI Agent Concept

Context Engineering, Prompt Context Composition, Working Memory, Episodic Memory.

## Prompt Engineering Note

context를 optional argument로 두어 backward compatibility를 유지하고, PromptAgent가 MemoryManager를 직접 호출하지 못하도록 책임 경계를 분리했습니다.

## Interview Talking Points

- 예상 질문: Context Engineering이란 무엇인가요?
- 예상 답변: agent가 사용할 정보를 선별하고 구성해 더 나은 prompt나 결정을 만들게 하는 작업입니다.
- 꼬리 질문: RAG와 어떻게 연결되나요?

## Future Work

RAG Style Library, Semantic Memory, Prompt Template Selection으로 확장합니다.
