# Meeting Log

## 2026-06-27 Sprint 7

이번 Sprint에서는 Reflection 구조를 채택했습니다. 이유는 생성 결과가 낮은 score를 받았을 때 단순히 실패로 끝내지 않고, 실패 원인을 분석하고 다음 prompt 개선 방향을 만들기 위해서입니다.

논의된 구조는 다음과 같습니다.

```text
Evaluation -> Reflection -> Retry Decision -> Memory
```

이번 단계에서는 실제 regeneration loop는 만들지 않았습니다. 대신 reflection 결과, retry 판단, memory 저장까지 연결해 다음 Sprint에서 loop를 안전하게 붙일 수 있는 기반을 만들었습니다.

## 2026-06-27 Memory Engineering Follow-up

이번 논의에서는 memory를 단순 파일 저장이 아니라 `MemoryManager` interface로 분리하기로 했습니다.

채택 이유:

- Orchestrator가 시작 시 과거 실행을 load할 수 있어야 합니다.
- 종료 시 현재 실행을 save해야 합니다.
- 전체 history 조회와 초기화가 가능한 interface가 필요합니다.
- 향후 database나 vector store로 바꿔도 orchestrator 코드를 크게 바꾸지 않는 구조가 필요합니다.

## 2026-06-27 Sprint 8 Retry Loop

이번 논의에서는 retry loop를 도입하되 1회로 제한하기로 결정했습니다. 목적은 reflection 결과가 실제 second attempt로 이어지는 self-improving flow를 검증하는 것입니다.

`RetryAgent`는 retry 여부만 판단하고, `OrchestratorAgent`가 generation/evaluation 재실행과 best result selection을 담당합니다.
