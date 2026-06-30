# Sprint 21: Semantic-like Memory Retrieval

## Objective

MemoryManager를 저장 전용 구조에서 검색 가능한 semantic-like memory layer로 확장한다.

## Problem

Agent가 이전 실행 기록을 저장하더라도 현재 요청과 유사한 과거 경험을 찾지 못하면 memory가 prompt 개선에 충분히 활용되지 않는다.

## Design Decision

JSON history 기반 keyword overlap similarity를 구현하고, `memory_retrieval` step을 DynamicExecutionEngine에 추가했다.

## Implementation Summary

- `MemoryManager.search_similar_runs()` 추가
- `MemoryManager.get_best_run()` 추가
- `MemoryManager.get_memory_context()` 추가
- `ExecutionEngine`이 `vision` 이후 `memory_retrieval` step을 자동 삽입
- `PromptCompressor`가 `memory_context`를 짧은 hint로 압축
- `PromptAgent`가 memory hint를 final prompt에 반영

## AI Agent Concept

Semantic-like Memory는 embedding 없이도 현재 요청과 과거 경험의 유사성을 계산해 prompt generation에 활용하는 구조다.

## Prompt Engineering Note

과거 run 전체를 prompt에 넣지 않고 `similar previous run found`, `memory match`, `reuse successful visual style` 같은 짧은 hint만 사용했다.

## Interview Talking Points

Q. 왜 Vector DB를 바로 쓰지 않았나요?
A. 먼저 memory retrieval interface와 workflow 위치를 검증하기 위해 JSON 기반으로 시작했습니다.

Q. 왜 memory retrieval이 vision 이후인가요?
A. caption이 생성된 뒤에야 image content와 user prompt를 결합한 query를 만들 수 있기 때문입니다.

## Future Work

- ChromaDB migration
- embedding-based similarity
- memory summarization
- typed memory schema
