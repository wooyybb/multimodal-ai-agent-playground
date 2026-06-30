# Sprint 21: Semantic-like Memory Retrieval

## Problem

MemoryManager가 실행 기록을 저장하고 있었지만, 현재 요청과 유사한 과거 경험을 검색하지 못했다. Orchestrator는 `load_last_run()` 중심으로 마지막 실행만 참고하고 있었다.

## Decision

JSON history 기반 keyword similarity search를 추가하고, `memory_retrieval` step을 도입했다.

## Alternatives

- 기존 `last_run`만 사용
- 바로 ChromaDB 도입
- SQLite 기반 검색
- LLM-based memory summarization

## Reason

MVP 단계에서는 JSON keyword similarity가 가장 단순하고 디버깅하기 쉽다. 동시에 `search_similar_runs()`, `get_best_run()`, `get_memory_context()` interface를 만들면 향후 Vector DB로 교체하기 쉽다.

## Future Work

- ChromaDB
- FAISS
- embedding-based search
- memory summarization
- long-term semantic memory
