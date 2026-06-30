# Sprint 20: Knowledge Manager & Retrieval Agent

## Objective

Prompt 생성 과정에 rule-based knowledge retrieval을 연결한다.

## Problem

기존 PromptAgent는 caption과 user prompt 중심으로 동작했기 때문에 style, lighting, composition 같은 domain knowledge를 체계적으로 활용하지 못했다.

## Design Decision

JSON 기반 Knowledge Store와 `KnowledgeManager`, `RetrievalAgent`를 추가했다. ExecutionEngine에는 `retrieval` step을 추가해 검색 결과를 `retrieved_context`로 state에 저장한다.

## Implementation Summary

- `knowledge/style_library.json` 추가
- `knowledge/lighting_rules.json` 추가
- `knowledge/composition_rules.json` 추가
- `knowledge/quality_rules.json` 추가
- `knowledge/negative_prompt_rules.json` 추가
- `agents/knowledge_manager.py` 추가
- `agents/retrieval_agent.py` 추가
- PlannerAgent execution plan에 `retrieval` step 추가
- OrchestratorAgent registry에 retrieval 등록
- PromptCompressor가 `retrieved_context`를 compressed hint로 병합

## AI Agent Concept

이번 Sprint는 Rule-based RAG의 시작이다. Knowledge Store는 지식을 저장하고, KnowledgeManager는 접근 interface를 제공하며, RetrievalAgent는 caption과 user prompt를 기반으로 필요한 rule을 찾는다.

## Prompt Engineering Note

PromptAgent에 knowledge rule을 직접 넣지 않고 RetrievalAgent와 PromptCompressor를 거치게 해서 prompt augmentation 책임을 분리했다.

## Interview Talking Points

Q. 왜 처음부터 ChromaDB를 쓰지 않았나요?
A. 먼저 Retrieval과 Augmentation의 책임을 분리하는 구조를 검증하기 위해 JSON으로 시작했습니다.

Q. KnowledgeManager는 왜 필요한가요?
A. RetrievalAgent가 storage details를 알지 않도록 Knowledge Layer interface를 제공하기 위해 필요합니다.

## Future Work

- Semantic Memory
- Vector DB integration
- Hybrid Retrieval
- RAG Style Library expansion
