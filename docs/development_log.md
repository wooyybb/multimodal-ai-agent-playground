# Development Log

## 2026-06-27

### Initial Project Structure

- 기본 Python 프로젝트 구조를 생성했습니다.
- `agents`, `tools`, `workflow`, `memory`, `ui`, `outputs` 폴더를 구성했습니다.
- 각 Python 패키지에는 `__init__.py`를 추가했습니다.
- 초기 파일은 TODO 수준의 skeleton으로 시작했습니다.

### VisionAgent Mock BLIP Tool

- `VisionAgent`를 구현했습니다.
- `VisionAgent`는 `BlipTool`을 호출하도록 구성했습니다.
- 실제 BLIP 모델은 아직 연결하지 않았고, `BlipTool`은 mock caption을 반환합니다.
- 현재 mock caption은 `"A girl standing in a park"`입니다.

### PromptAgent

- `PromptAgent`를 구현했습니다.
- `caption`과 `user_prompt`를 조합해 `final_prompt`를 생성합니다.
- 빈 `user_prompt`가 들어오면 caption 기반 prompt만 생성하도록 처리했습니다.

### OrchestratorAgent And ReflectionAgent

- `OrchestratorAgent`를 추가했습니다.
- 기존 `MultimodalPipeline`이 직접 agent를 호출하던 구조에서, `OrchestratorAgent`가 `VisionAgent`와 `PromptAgent`를 조율하는 구조로 변경했습니다.
- `ReflectionAgent`를 mock 형태로 추가했습니다.
- 현재는 실제 model integration 없이 Python class 기반 multi-agent 구조를 만드는 단계입니다.

### GenerationAgent Mock Image Generation

- `GenerationAgent`를 구현했습니다.
- `GenerationAgent`는 `FluxTool`을 호출하도록 구성했습니다.
- 실제 FLUX API 또는 HuggingFace API는 연결하지 않았습니다.
- `FluxTool`은 PIL을 사용해 `outputs/output_mock.png` mock image를 생성하고 저장 경로를 반환합니다.
- `OrchestratorAgent` 실행 순서를 `VisionAgent -> PromptAgent -> GenerationAgent`로 확장했습니다.

### EvaluationAgent Mock CLIP Evaluation

- `EvaluationAgent`를 구현했습니다.
- `EvaluationAgent`는 `ClipTool`을 호출하도록 구성했습니다.
- 실제 CLIP 모델은 로드하지 않았습니다.
- `ClipTool`은 generated image file 존재 여부와 final prompt 길이를 활용해 0.0~1.0 사이 deterministic mock score를 반환합니다.
- `OrchestratorAgent` 실행 순서를 `VisionAgent -> PromptAgent -> GenerationAgent -> EvaluationAgent`로 확장했습니다.

### ReflectionAgent And RetryAgent

- `RetryAgent`를 구현했습니다.
- 기본 threshold는 `0.75`로 설정했습니다.
- score가 threshold보다 낮으면 retry 필요 여부를 `True`로 반환합니다.
- `ReflectionAgent`를 rule-based mock reflection 구조로 확장했습니다.
- score가 `0.75` 미만이면 개선 제안과 `suggested_prompt`를 반환하고, `0.75` 이상이면 `"no major revision needed"`를 반환합니다.
- 실제 재생성 loop는 아직 구현하지 않았고, retry 여부와 suggested prompt까지만 반환합니다.

### Sprint 7 Reflection Retry Memory

- `OrchestratorAgent` 호출 순서를 `Evaluation -> Reflection -> Retry -> Memory`로 정리했습니다.
- `Memory` layer를 `memory/history.py`에 구현했습니다.
- 실행 기록은 `memory/history.json`에 저장합니다.
- 저장 항목은 `caption`, `prompt`, `score`, `reflection`, `retry`, `timestamp`입니다.
- 이번 Sprint는 실제 regeneration loop가 아니라 self-improving agent architecture의 feedback loop contract를 만드는 데 집중했습니다.

### Sprint 7 Memory Engineering

- `History` 저장 유틸을 `MemoryManager` interface로 확장했습니다.
- `load_last_run()`, `save_run()`, `get_history()`, `clear_history()` 메서드를 구현했습니다.
- `OrchestratorAgent`는 시작 시 `load_last_run()`을 호출하고, 종료 시 `save_run()`을 호출합니다.
- `history.json` 저장 항목에 `output_image_path`를 추가했습니다.
- `save_run(record: dict)` 형태로 Memory Interface를 정리했습니다.
- 반환 dict에 `last_run`과 `memory_saved`를 추가했습니다.
- 이번 작업은 working memory, episodic memory, state management, agent context를 코드와 문서에 연결하는 데 집중했습니다.

### Sprint 8 One-Step Retry Loop

- `OrchestratorAgent`에 1회 retry loop를 구현했습니다.
- initial generation과 initial evaluation 이후 `ReflectionAgent`가 `suggested_prompt`를 생성합니다.
- `RetryAgent`가 retry 여부만 판단하고, 실제 second attempt 실행은 `OrchestratorAgent`가 제어합니다.
- retry가 필요한 경우 `suggested_prompt`로 `GenerationAgent`와 `EvaluationAgent`를 한 번 더 실행합니다.
- initial result와 retry result 중 더 높은 score를 best result로 선택합니다.
- `MemoryManager`는 initial, retry, best 정보를 포함한 full retry record를 저장합니다.

### Sprint 9 Gradio UI Integration

- `main.py`를 Gradio app 실행 진입점으로 구성했습니다.
- `ui/app.py`에 `create_app()`을 구현했습니다.
- UI는 `MultimodalPipeline.run(image, user_prompt)`만 호출하도록 구성했습니다.
- image input, user prompt, caption, final prompt, initial/retry/best image, score, reflection, retry status, agent trace를 표시합니다.
- image가 비어 있거나 workflow 예외가 발생할 때 UI에 안내 메시지를 반환하도록 처리했습니다.

### Sprint 10 Real BLIP Integration

- `BlipTool`을 실제 BLIP captioning tool로 확장했습니다.
- 모델은 `Salesforce/blip-image-captioning-base`를 사용합니다.
- `VisionAgent` interface는 `run(image) -> str`로 유지했습니다.
- BLIP model과 processor는 `_load_model()`에서 lazy loading합니다.
- 이미지 입력은 PIL image, file path, Gradio image 입력을 처리할 수 있도록 RGB 변환을 수행합니다.
- BLIP 로딩 또는 inference 실패 시 fallback caption `"An uploaded image"`를 반환합니다.

### Sprint 11 Real FLUX Integration

- `FluxTool`을 Hugging Face `InferenceClient` 기반 FLUX generation 구조로 확장했습니다.
- 모델은 `black-forest-labs/FLUX.1-schnell`을 사용합니다.
- `HF_TOKEN`이 있으면 real FLUX generation을 시도합니다.
- `HF_TOKEN`이 없거나 API 호출이 실패하면 PIL 기반 fallback mock image를 생성합니다.
- output file name은 timestamp 기반으로 생성해 중복 저장을 방지합니다.
- `GenerationAgent.run(final_prompt) -> str` interface는 유지했습니다.

### Sprint 12 Real CLIP Evaluation

- `ClipTool`을 실제 CLIP image-text similarity evaluation tool로 확장했습니다.
- 모델은 `openai/clip-vit-base-patch32`를 사용합니다.
- CLIP model과 processor는 `_load_model()`에서 lazy loading합니다.
- generated image와 final prompt를 같은 embedding space에서 비교합니다.
- cosine similarity를 `(similarity + 1) / 2` 방식으로 0.0~1.0 범위 score로 변환합니다.
- CLIP 로딩 또는 inference 실패 시 fallback score `0.0`을 반환합니다.

### Sprint 13 Integration And Validation

- 새 기능 추가보다 End-to-End validation과 demo readiness에 집중했습니다.
- UI output이 `None` 값으로 깨지지 않도록 defensive formatting을 추가했습니다.
- score는 UI 출력 전에 소수점 4자리 기준으로 정리합니다.
- `agent_trace`는 항상 list 기반으로 받고 줄바꿈 문자열로 표시합니다.
- memory 저장 실패가 전체 workflow를 중단하지 않도록 Orchestrator에서 방어 처리했습니다.
- `docs/testing.md`, `docs/known_issues.md`, `docs/demo_script.md`를 추가했습니다.

### CLIP Similarity Tensor Extraction Bug Fix

- CLIP evaluation에서 model output 객체를 cosine similarity에 직접 전달할 수 있는 위험을 수정했습니다.
- `CLIPModel.get_image_features()`와 `CLIPModel.get_text_features()`로 tensor feature를 추출하도록 명확히 했습니다.
- image/text feature를 `torch.nn.functional.normalize(..., dim=-1)`로 정규화한 뒤 cosine similarity를 계산합니다.
- similarity는 `(similarity + 1.0) / 2.0`으로 0.0~1.0 범위 score로 변환합니다.

### CLIP Feature Extraction Fix

- `BaseModelOutputWithPooling` 객체에 normalize/norm 연산이 적용되는 문제를 방지했습니다.
- `self.model(**inputs)`, `outputs.image_embeds`, `outputs.text_embeds`를 사용하지 않고 `get_image_features()`와 `get_text_features()`만 사용하도록 정리했습니다.
- feature Tensor를 `F.normalize(..., p=2, dim=-1)`로 정규화한 뒤 `torch.sum(image_features * text_features, dim=-1).item()`으로 cosine 값을 계산합니다.
