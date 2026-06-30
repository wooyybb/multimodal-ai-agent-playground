# Sprint 20: Knowledge Manager & Retrieval Agent

## Problem

PromptAgent는 caption, compressed context, user prompt만 사용하고 있었다. 하지만 `anime`, `cinematic`, `portrait` 같은 표현은 단순 문자열이 아니라 prompt rule과 domain knowledge로 해석되어야 한다.

## Decision

Vector DB를 바로 도입하지 않고 JSON 기반 Knowledge Store, `KnowledgeManager`, `RetrievalAgent`를 먼저 구현했다.

## Alternatives

- PromptAgent 내부에 rule을 직접 작성
- 처음부터 ChromaDB 또는 FAISS 도입
- LLM에게 style rule 생성을 맡김
- 기존 compressed context만 유지

## Reason

RAG의 핵심은 Vector DB가 아니라 Retrieval과 Augmentation의 분리다. JSON Knowledge Store로 시작하면 구조를 단순하게 유지하면서도 향후 ChromaDB, FAISS, Milvus 같은 storage layer로 교체하기 쉽다.

## Future Work

- ChromaDB 또는 FAISS 기반 semantic search
- user preference memory와 knowledge retrieval 결합
- hybrid retrieval
- knowledge scoring
- style rule versioning
