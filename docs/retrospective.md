# Retrospective

## 잘된 점

- Reflection, Retry, Memory의 책임을 분리했습니다.
- 실제 LLM이나 무거운 라이브러리 없이 feedback loop contract를 만들었습니다.
- `history.json` 저장으로 향후 개선 분석의 기반을 마련했습니다.

## 아쉬운 점

- 아직 실제 regeneration loop는 없습니다.
- Reflection은 rule-based mock이라 복잡한 실패 원인을 분석하지는 못합니다.
- Memory는 append-only JSON 저장이라 검색이나 요약 기능은 없습니다.

## 다음 Sprint

- 실제 retry loop 연결
- retry 횟수 제한과 stop condition 설계
- memory history를 활용한 prompt 개선 로직 설계

## Memory Engineering Follow-up

### 잘된 점

- `MemoryManager` interface가 명확해졌습니다.
- `load_last_run()`과 `save_run()`이 orchestrator lifecycle에 연결됐습니다.
- `history.json`이 episodic memory 역할을 하도록 확장됐습니다.

### 아쉬운 점

- 아직 memory를 prompt 생성이나 reflection 개선에 직접 사용하지는 않습니다.
- JSON 파일이 커질 때의 성능 대책은 없습니다.

### 다음 Sprint

- last run context를 `PromptAgent` 또는 `ReflectionAgent`에 활용
- retry loop 실행 시 memory에 attempt 단위 기록 저장
- JSONL 또는 SQLite 전환 검토
