# Prompt Archive 021: Semantic-like Memory Retrieval

## Purpose

이번 prompt는 MemoryManager를 단순 저장소에서 검색 가능한 memory layer로 확장하기 위한 architecture prompt다.

## Summary

Vector DB 없이 JSON history를 기반으로 keyword overlap similarity를 구현하고, `vision` 이후 `memory_retrieval` step에서 현재 caption과 user prompt에 유사한 과거 실행을 찾도록 설계했다.

## Key Constraints

- Vector DB 사용 금지
- PlannerAgent 수정 금지
- full history를 prompt에 직접 넣지 않기
- prompt budget 유지
- old history schema와 backward compatibility 유지

## Prompt Engineering Note

이번 prompt는 memory retrieval 위치와 prompt budget 제한을 명확히 지정했다. caption이 있어야 더 좋은 query가 만들어지므로 `memory_retrieval`은 `vision` 이후에 배치했다.
