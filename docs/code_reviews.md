# Code Reviews

## Sprint 7 Review

### Findings

- 현재 `ReflectionAgent`와 `RetryAgent`는 같은 threshold `0.75`를 사용합니다. 향후 threshold를 변경할 때 두 agent의 기준이 어긋나지 않도록 shared config 또는 orchestrator-level policy를 고려할 수 있습니다.
- `Memory`는 `history.json` 전체를 읽고 다시 쓰는 단순 구조입니다. 기록이 커지면 JSONL 또는 database 방식으로 변경하는 것이 좋습니다.
- 실제 retry loop는 아직 구현하지 않았으므로 `retry_needed`는 decision signal로만 사용됩니다.

### Summary

Sprint 7에서는 architecture contract가 명확해졌습니다. `Evaluation -> Reflection -> Retry -> Memory` 흐름이 코드와 문서 모두에 반영되었습니다.

## Sprint 7 Memory Engineering Review

### Findings

- `MemoryManager`는 JSON 전체를 읽고 다시 쓰는 구조입니다. 초기에는 단순하고 검증하기 좋지만, history가 커지면 JSONL 또는 SQLite가 더 적합합니다.
- `load_last_run()`은 현재 반환값에 포함되지만 아직 agent decision에 직접 쓰이지 않습니다. 다음 단계에서 prompt generation 또는 reflection context로 연결할 수 있습니다.
- `clear_history()`는 구현됐지만 orchestrator에서는 호출하지 않습니다. 테스트나 UI에서 명시적 초기화 기능으로 연결하는 것이 좋습니다.

### Summary

Memory가 단순 저장 파일에서 명시적 interface로 바뀌었습니다. 이 변화로 향후 storage backend를 교체하거나 memory retrieval을 추가하기 쉬워졌습니다.

## Sprint 7 Attachment Review

### Findings

- `MemoryManager.save_run()`은 이제 `record: dict`를 받습니다. schema validation은 아직 없으므로 이후 필수 key 검증을 추가할 수 있습니다.
- `memory_saved`는 save 성공 시 `True`로 반환됩니다. 예외 처리와 실패 시 `False` 반환은 다음 단계에서 보강할 수 있습니다.
- Orchestrator만 memory에 접근하는 구조는 적절합니다. 다만 last run을 실제 prompt/reflection context로 활용하는 단계는 아직 남아 있습니다.

## Sprint 8 Retry Loop Review

### Findings

- Retry는 1회로 제한되어 infinite loop 위험이 낮습니다.
- `RetryAgent`는 `should_retry()`만 담당하고, second attempt 실행은 `OrchestratorAgent`가 담당해 책임 분리가 유지됩니다.
- `GenerationAgent` mock은 같은 `outputs/output_mock.png` 경로를 반환하므로 initial/retry image path가 같을 수 있습니다. 실제 generation 도입 시 attempt별 파일명을 분리하는 것이 좋습니다.
- best result selection은 score 비교 기반입니다. 동점에서는 initial result를 유지합니다.

## Sprint 9 Gradio UI Review

### Findings

- UI가 `MultimodalPipeline`만 호출하므로 agent orchestration 책임이 UI로 섞이지 않습니다.
- `image is None` 입력에 대한 사용자 안내가 있습니다.
- workflow 예외는 UI message로 반환됩니다. 향후에는 traceback logging을 별도 파일이나 console에 남길 수 있습니다.
- Gradio output image는 path 기반으로 처리합니다. output path가 `None`이면 image output도 `None`으로 유지됩니다.

## Sprint 10 Real BLIP Review

### Findings

- `BlipTool`은 lazy loading을 사용하므로 import 시점에 heavy model을 로드하지 않습니다.
- `transformers` 또는 model loading 실패 시 fallback caption을 반환합니다.
- `VisionAgent`는 tool 호출만 유지해 Tool-Agent Separation이 지켜졌습니다.
- 실제 BLIP inference는 모델 다운로드와 runtime dependency가 필요하므로, 오프라인 환경에서는 fallback path가 동작합니다.

## Sprint 11 Real FLUX Review

### Findings

- `FluxTool`은 `HF_TOKEN`이 있을 때만 real API generation을 시도합니다.
- token이 없거나 API 호출이 실패하면 fallback image를 생성해 workflow가 멈추지 않습니다.
- output filename은 timestamp 기반이라 이전 output을 덮어쓰지 않습니다.
- API token은 `.env.example`에 placeholder만 제공하고 실제 secret은 저장하지 않습니다.
