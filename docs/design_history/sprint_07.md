# Sprint 7 Design History

## 문제

현재 agent workflow는 이전 실행 결과를 기억하지 못합니다. Reflection과 Retry가 의미 있으려면 이전 prompt, score, reflection, retry 결과를 저장하고 다시 읽을 수 있어야 합니다.

## 결정

`memory/history.py`에 `MemoryManager`를 도입했습니다. Orchestrator는 시작 시 `load_last_run()`을 호출하고, 종료 시 `save_run()`을 호출합니다.

## 대안

- 기존 `History.save()`만 유지
- Memory를 별도 Agent로 구현
- SQLite 또는 vector database를 즉시 도입

## 채택 이유

현재 단계에서는 architecture와 interface가 중요합니다. JSON 기반 `MemoryManager`는 dependency 없이 빠르게 검증할 수 있고, 향후 database로 바꾸더라도 orchestrator의 사용 방식은 유지할 수 있습니다.

## 향후 개선

- JSONL 또는 SQLite 저장소 검토
- last run을 `PromptAgent`와 `ReflectionAgent` context로 전달
- retry attempt별 memory schema 설계
- summary memory와 vector memory 분리

## Implementation Note

`MemoryManager`는 `load_last_run()`, `save_run(record: dict)`, `get_history()`, `clear_history()` interface를 제공합니다. Memory 접근은 `OrchestratorAgent`가 담당하고, 개별 agent는 memory 저장소에 직접 접근하지 않습니다.
