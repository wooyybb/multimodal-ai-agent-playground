# Code Reviews

## Sprint 7 Review

### Findings

- 현재 `ReflectionAgent`와 `RetryAgent`는 같은 threshold `0.75`를 사용합니다. 향후 threshold를 변경할 때 두 agent의 기준이 어긋나지 않도록 shared config 또는 orchestrator-level policy를 고려할 수 있습니다.
- `Memory`는 `history.json` 전체를 읽고 다시 쓰는 단순 구조입니다. 기록이 커지면 JSONL 또는 database 방식으로 변경하는 것이 좋습니다.
- 실제 retry loop는 아직 구현하지 않았으므로 `retry_needed`는 decision signal로만 사용됩니다.

### Summary

Sprint 7에서는 architecture contract가 명확해졌습니다. `Evaluation -> Reflection -> Retry -> Memory` 흐름이 코드와 문서 모두에 반영되었습니다.
