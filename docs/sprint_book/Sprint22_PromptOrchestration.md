# Sprint 22: Multi-Agent Prompt Orchestration Framework

## Objective

PromptAgent 하나가 모든 prompt engineering을 처리하던 구조를 여러 전문 agent가 협업하는 Prompt Orchestration Framework로 확장한다.

## Problem

기존 PromptAgent는 caption, retrieval, memory, planner, user prompt를 한 번에 처리했다. 하지만 실제 image generation prompt는 character, style, layout, lighting, negative prompt처럼 서로 다른 역할을 가진 요소로 구성된다.

## Design Decision

`CharacterAgent`, `StyleAgent`, `LayoutAgent`, `LightingAgent`, `NegativePromptAgent`, `PromptAssembler`를 추가했다. 각 agent는 자기 역할의 prompt fragment를 만들고, PromptAssembler가 generation prompt를 조립한다.

## Implementation Summary

- role-based prompt agents 추가
- Planner execution plan에 prompt orchestration steps 추가
- OrchestratorAgent ToolRegistry에 새 agents 등록
- ExecutionEngine에 각 prompt step handler 추가
- PromptAssembler가 generation prompt를 생성

## AI Agent Concept

Prompt Orchestration은 하나의 agent가 모든 prompt를 만드는 대신, 여러 역할 기반 agent가 부분 결과를 만들고 assembler가 최종 prompt를 구성하는 협업 구조다.

## Prompt Engineering Note

Agent context 전체를 prompt에 넣지 않고, 각 agent가 생성한 prompt fragment만 Generation Prompt에 사용한다.

## Interview Talking Points

Q. 왜 PromptAgent 하나가 아니라 여러 Agent로 나누었나요?
A. style, character, layout, lighting, negative prompt는 서로 다른 prompt engineering 책임이기 때문입니다.

Q. PromptAssembler는 왜 필요한가요?
A. 여러 agent의 fragment를 하나의 일관된 generation prompt로 조립하는 책임이 필요하기 때문입니다.

Q. Prompt Routing이란?
A. prompt 생성 책임을 역할에 따라 적절한 agent로 보내는 구조입니다.

## Future Work

- LLM-based prompt routing
- richer character parsing
- typed prompt fragment schema
- prompt quality evaluator
## Detailed Update

The implemented Sprint22 structure includes CharacterAgent, StyleAgent, LayoutAgent, PoseAgent, ExpressionAgent, LightingAgent, NegativePromptAgent, and PromptAssembler. PromptAssembler outputs `generation_prompt`, `negative_prompt`, and `prompt_sections`.
