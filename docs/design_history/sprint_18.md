# Sprint 18 Design History

## Problem

Sprint 17에서 PromptAgent는 Planner와 Memory에서 온 context를 prompt에 반영할 수 있게 되었다. 하지만 raw context를 그대로 prompt에 붙이면 prompt가 길어지고, CLIP text encoder의 77 token 제한에 가까워지는 문제가 생긴다.

## Decision

`PromptCompressor`를 추가해 raw context를 짧은 semantic hint로 압축한다.

## Alternatives

- PromptAgent 내부에서 직접 context를 줄이는 방식
- OrchestratorAgent가 context 문자열을 직접 만드는 방식
- Context를 사용하지 않고 caption과 user prompt만 사용하는 방식

## Adopted Reason

PromptAgent는 prompt composition에 집중하고, PromptCompressor는 context selection과 compression에 집중하도록 책임을 분리했다. 이 구조는 향후 RAG, Semantic Memory, LLM 기반 Planner가 들어와도 prompt budget 관리 지점을 명확하게 유지한다.

## Future Improvements

- RAG Style Library를 붙여 style hint를 검색 기반으로 생성
- Semantic Memory에서 높은 점수의 스타일 패턴만 선택
- LLM Planner가 token budget을 고려해 필요한 context만 요청
