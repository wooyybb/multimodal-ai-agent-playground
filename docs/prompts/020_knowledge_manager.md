# Prompt Archive 020: Knowledge Manager & Retrieval Agent

## Purpose

이번 prompt는 Prompt 생성 과정에 external knowledge를 연결하기 위한 rule-based RAG architecture prompt다.

## Summary

Vector DB 없이 `knowledge/*.json`, `KnowledgeManager`, `RetrievalAgent`를 도입하고, ExecutionEngine에 `retrieval` step을 추가해 PromptCompressor와 PromptAgent가 검색된 knowledge를 사용할 수 있게 한다.

## Prompt Constraints

- tools, memory, ui, main, README, requirements 수정 금지
- JSON Knowledge Store부터 시작
- RetrievalAgent가 JSON을 직접 읽지 않고 KnowledgeManager를 통해 접근
- workflow는 계속 진행되어야 하며 knowledge load 실패 시 빈 dict 반환

## Prompt Engineering Note

이번 prompt는 storage layer와 retrieval responsibility를 분리하도록 설계되었다. Codex가 Vector DB를 성급하게 붙이지 않고, 확장 가능한 RAG skeleton을 먼저 만들도록 유도했다.
