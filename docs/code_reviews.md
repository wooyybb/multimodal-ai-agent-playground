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

## Sprint 12 Real CLIP Review

### Findings

- `ClipTool`은 lazy loading을 사용해 import 시점에 CLIP model을 로드하지 않습니다.
- generated image path나 final prompt가 비어 있으면 fallback score `0.0`을 반환합니다.
- reference image는 interface에 유지되지만 이번 Sprint에서는 사용하지 않습니다.
- CLIP score는 prompt alignment signal이며, aesthetic quality를 완전히 대체하지는 않습니다.

## Sprint 13 Integration Review

### Findings

- UI는 missing key와 `None` output에 대해 defensive formatting을 수행합니다.
- `agent_trace`는 list가 아니어도 빈 list로 정리되어 UI가 깨지지 않습니다.
- memory save 실패는 전체 workflow를 중단하지 않고 `memory_saved=False`로 반영됩니다.
- E2E validation은 문서 기반 체크리스트로 정리됐지만, 아직 자동화된 test suite는 없습니다.

## CLIP Similarity Bug Fix Review

### Findings

- 원인: CLIP evaluation에서 `BaseModelOutputWithPooling` 같은 model output 객체를 tensor처럼 cosine similarity에 전달하면 `cosine_similarity(): argument 'x1' must be Tensor` 오류가 발생할 수 있습니다.
- 수정: `get_image_features()`와 `get_text_features()`를 사용해 tensor feature를 추출하고, 두 feature를 `F.normalize(..., dim=-1)` 방식으로 정규화한 뒤 cosine similarity를 계산했습니다.
- fallback: CLIP loading 또는 inference 중 예외가 발생하면 기존처럼 fallback score `0.0`을 반환합니다.

## CLIP BaseModelOutputWithPooling Bug Review

### Findings

- 원인: CLIP model output 객체인 `BaseModelOutputWithPooling`을 feature Tensor처럼 다루면 `.norm` attribute 오류가 발생합니다.
- 수정: `self.model(**inputs)` 결과나 `outputs.image_embeds`/`outputs.text_embeds`를 사용하지 않고, `get_image_features()`와 `get_text_features()`의 반환 Tensor만 사용하도록 고정했습니다.
- 계산: image/text feature를 `F.normalize(..., p=2, dim=-1)`로 정규화하고 `torch.sum(image_features * text_features, dim=-1).item()`으로 cosine 값을 구합니다.

## Sprint 15 PlannerAgent Review

### Findings

- PlannerAgent는 execution plan만 생성하고 직접 실행하지 않아 책임 분리가 유지됩니다.
- OrchestratorAgent는 기존 fixed workflow를 유지하면서 planner_result를 기록합니다.
- 현재 plan은 dynamic execution에 사용되지 않으므로, plan과 실제 실행 흐름이 어긋나지 않도록 향후 validation이 필요합니다.
- LLM planner 도입 전 rule-based planner로 시작한 점은 디버깅과 설명 가능성 측면에서 적절합니다.

## Sprint 16 ToolRegistry Review

### Findings

- `ToolRegistry.call()`은 run method가 있으면 `run()`을 호출하고, callable이면 직접 호출합니다.
- 등록되지 않은 tool name은 `ValueError`를 발생시켜 실패 원인이 명확합니다.
- Orchestrator는 기존 순서를 유지하되 registry 호출로 감싸 결합도를 낮췄습니다.
- 아직 plan을 for-loop로 실행하지 않으므로 dynamic execution validation은 다음 Sprint 과제입니다.

## Sprint 17 Context Engineering Review

### Findings

- `PromptAgent.run()`은 `context=None` 기본값을 가져 기존 호출과 호환됩니다.
- PromptAgent가 MemoryManager나 PlannerAgent를 직접 호출하지 않아 책임 분리가 유지됩니다.
- context 정보는 prompt에 짧게 반영되지만, 너무 많은 previous prompt가 들어가지 않도록 length limit을 적용했습니다.
- context dict는 유연하지만 schema validation은 아직 없습니다.
## Sprint 18 Code Review

- `PromptCompressor`는 planner reason과 previous best prompt 전체를 prompt에 넣지 않고 짧은 hint만 반환합니다.
- `PromptAgent`는 `compressed_context`만 사용하도록 변경되어 context leakage 위험이 줄었습니다.
- `OrchestratorAgent`는 기존 workflow를 유지하면서 PromptCompressor 호출을 PromptAgent 앞에 추가했습니다.
- 남은 리스크: 실제 tokenizer 기준 token count가 아니라 word/character 기반 제한이므로, 향후 tokenizer-aware budget 관리가 필요합니다.
## Sprint 19 Code Review

- OrchestratorAgent가 직접 step을 실행하지 않고 DynamicExecutionEngine에 위임하도록 변경되었습니다.
- ExecutionEngine은 step별 handler를 통해 state transition을 관리합니다.
- unknown step은 trace에 기록하고 skip합니다.
- memory_save 실패는 workflow 전체를 중단하지 않도록 처리했습니다.
- 남은 리스크: state dict key가 문자열 기반이라 typo에 취약하므로 향후 typed schema 도입을 검토해야 합니다.
