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
- Hugging Face token 환경변수가 있으면 real FLUX generation을 시도합니다.
- Hugging Face token 환경변수가 없거나 API 호출이 실패하면 PIL 기반 fallback mock image를 생성합니다.
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

### README And Demo Documentation

- README를 현재 End-to-End multi-agent workflow 기준으로 정리했습니다.
- setup, `.env` 설정, `python main.py` 실행 방법을 추가했습니다.
- demo screenshots/images는 `assets/demo/`에 선별 보관하고, `outputs/` 전체를 Git에 올리지 않는 방향을 명시했습니다.
- demo script와 interview notes를 최신 BLIP/FLUX/CLIP/Memory 구조에 맞춰 보강했습니다.

### Sprint 15 PlannerAgent

- rule-based `PlannerAgent`를 추가했습니다.
- `PlannerAgent.run(user_prompt, image_provided)`는 task type, requirement flags, execution plan, reason을 반환합니다.
- `OrchestratorAgent`는 workflow 시작 시 `PlannerAgent`를 호출하고 `planner_result`를 반환 dict에 포함합니다.
- agent trace에 `PlannerAgent generated execution plan` 단계를 추가했습니다.
- 이번 Sprint에서는 dynamic execution engine을 만들지 않고 기존 fixed workflow를 유지했습니다.

### Sprint Book Generator v2

- `docs/templates/`에 Sprint, Interview, Retrospective, Design History, Prompt Archive, Code Review 템플릿을 추가했습니다.
- `docs/sprint_book/`에 Sprint00부터 Sprint14까지의 Sprint Book 문서를 생성했습니다.
- 각 Sprint 문서는 Objective, Background, Problem, Design Decision, Architecture, Implementation Summary, AI Agent Concept, Prompt Engineering Note, Codex Usage, Debugging Experience, Interview Talking Points, Lessons Learned, Future Work 형식을 따릅니다.
- Sprint Book README에 project vision, phase, sprint index, architecture evolution, learning journey, interview usage를 정리했습니다.
- 앞으로 Sprint -> Code -> Documentation -> Interview Notes -> Retrospective -> Prompt Archive -> Commit 흐름을 반복 가능한 문서화 프로세스로 관리할 수 있게 했습니다.

### Sprint 16 Tool Registry

- `registry/` 패키지를 추가했습니다.
- `ToolRegistry`에 `register`, `call`, `list_tools`, `has_tool` 메서드를 구현했습니다.
- `OrchestratorAgent`가 기존 Agent와 MemoryManager 호출을 registry에 등록하도록 변경했습니다.
- 기존 workflow 순서는 유지하되 각 단계 호출을 `registry.call(...)`로 감쌌습니다.
- agent trace에 ToolRegistry 호출 단계를 기록하도록 수정했습니다.

### Sprint 17 Context Engineering

- `PromptAgent.run(caption, user_prompt, context=None)` 형태로 backward compatible하게 확장했습니다.
- `OrchestratorAgent`가 `planner_result`, `last_run`, `previous_best_prompt`, `previous_best_score`를 포함한 context dict를 구성합니다.
- `PromptAgent`는 context를 참고하되 과도하게 복사하지 않고 짧은 context note만 final prompt에 반영합니다.
- agent trace에 `OrchestratorAgent built prompt context`와 `PromptAgent generated context-aware prompt`를 추가했습니다.
## Sprint 18: Prompt Compression & Context Budget Management

- `PromptCompressor`를 추가해 Planner와 Memory에서 온 raw context를 짧은 `compressed_context`로 변환했습니다.
- `PromptAgent`는 raw context 대신 압축된 hint만 사용하도록 변경했습니다.
- Prompt 길이를 40~60 words 수준으로 유지하도록 제한해 CLIP 77 token 문제를 완화했습니다.
- Orchestrator 흐름을 Planner -> Context Builder -> PromptCompressor -> PromptAgent 순서로 정리했습니다.
## Sprint 19: Dynamic Execution Engine

- `workflow/execution_engine.py`에 `DynamicExecutionEngine`을 추가했습니다.
- PlannerAgent의 `execution_plan`에 `prompt_compressor` step을 포함했습니다.
- OrchestratorAgent의 고정 step 실행 로직을 제거하고 ExecutionEngine에 위임했습니다.
- Runtime state dict를 통해 각 step의 입력과 출력을 관리하도록 변경했습니다.
- 기존 one-step retry와 memory save 흐름은 유지했습니다.
## Sprint 20: Knowledge Manager & Retrieval Agent

- JSON 기반 Knowledge Store를 `knowledge/` 폴더에 추가했습니다.
- `KnowledgeManager`를 통해 style, lighting, composition, quality, negative prompt rule을 로드하도록 했습니다.
- `RetrievalAgent`를 추가해 caption과 user prompt 기반 rule-based retrieval을 수행했습니다.
- PlannerAgent execution plan에 `retrieval` step을 추가했습니다.
- ExecutionEngine이 retrieval 결과를 `retrieved_context`로 state에 저장하도록 했습니다.
- PromptCompressor가 retrieved context를 compressed hint로 병합하도록 업데이트했습니다.
## CLIP-Safe Evaluation Prompt Separation

- retry prompt를 55 words로 줄여도 CLIP tokenizer 기준 77 token 제한을 넘을 수 있는 문제가 확인되었습니다.
- `PromptCompressor.make_evaluation_prompt()`를 추가해 CLIP evaluation 전용 prompt를 별도로 생성하도록 했습니다.
- `DynamicExecutionEngine`은 generation에는 `final_prompt`/`retry_prompt`를 사용하고, evaluation에는 `evaluation_prompt`/`retry_evaluation_prompt`를 사용하도록 분리했습니다.
- state에 `evaluation_prompt`와 `retry_evaluation_prompt`를 저장하도록 변경했습니다.

## Retry Prompt Compression Bug Fix

- Sprint20 이후 retrieved context가 prompt에 반영되면서 retry reflection prompt가 길어지는 문제가 발견되었습니다.
- `PromptCompressor.compress_prompt()`를 추가해 retry prompt를 55 words 이하로 제한했습니다.
- `DynamicExecutionEngine`은 `raw_suggested_prompt`를 보존하고, generation/evaluation에는 compressed `retry_prompt`를 사용하도록 수정했습니다.
- memory save record에 raw suggested prompt와 compressed retry prompt를 구분해 저장하도록 업데이트했습니다.
## Sprint 21: Semantic-like Memory Retrieval

- `MemoryManager.search_similar_runs()`를 추가했습니다.
- `MemoryManager.get_best_run()`과 `get_memory_context()`를 추가했습니다.
- `DynamicExecutionEngine`이 `vision` 이후 `memory_retrieval` step을 자동 삽입하도록 변경했습니다.
- `OrchestratorAgent`가 `memory_retrieval` tool을 registry에 등록하도록 변경했습니다.
- `PromptCompressor`가 `memory_context`를 짧은 memory hint로 압축하도록 업데이트했습니다.
- `PromptAgent`가 memory hint를 final prompt에 반영하도록 업데이트했습니다.
## Sprint 22: Multi-Agent Prompt Orchestration Framework

- `CharacterAgent`, `StyleAgent`, `LayoutAgent`, `LightingAgent`, `NegativePromptAgent`를 추가했습니다.
- `PromptAssembler`를 추가해 role-based prompt fragment를 generation prompt로 조립하도록 했습니다.
- Planner execution plan에 prompt orchestration steps를 추가했습니다.
- OrchestratorAgent ToolRegistry에 새 prompt agents를 등록했습니다.
- ExecutionEngine에 character/style/layout/lighting/negative_prompt/prompt_assembler step을 추가했습니다.
## Sprint22 Detailed Prompt Orchestration Update

- Added `PoseAgent` and `ExpressionAgent`.
- Updated role agents to return section dicts instead of loose lists.
- Updated `PromptAssembler` to return `generation_prompt`, `negative_prompt`, and `prompt_sections`.
- Updated `ExecutionEngine` to store `character_section`, `style_section`, `layout_section`, `pose_section`, `expression_section`, and `negative_section`.
- Kept GenerationAgent, EvaluationAgent, ReflectionAgent, RetryAgent, VisionAgent unchanged.
## Sprint23: Character Reference Handling

- Extended `CharacterAgent` to return `character_count`, `characters`, and `global_character_rules`.
- Added fallback for single-image workflow with `character_count=1`.
- Added prompt-based multi-character hints such as `two characters`, `friends`, `couple`, and `photobooth`.
- Updated `PromptAssembler` to add compact character preservation rules to `generation_prompt`.
- Kept UI and model agents unchanged.
## Sprint24: Layout Planning Agent

- Changed `LayoutAgent` from keyword generation to layout planning.
- Added layout type detection for photobooth, scrapbook, poster, profile, portrait, illustration, sticker sheet, concept sheet, comic page, and cinematic layouts.
- Added camera view, subject placement, background style, and composition rules.
- Updated `PromptAssembler` to convert Layout Plan into generation prompt phrases.
## Sprint25: Scene Planning Agent

- Added `ScenePlanningAgent`.
- Added `scene_planning` step to Planner and ExecutionEngine.
- Orchestrator registers `scene_planning`.
- LayoutAgent reflects scene_type and camera intent.
- PoseAgent reflects relationship, interaction, and energy.
- ExpressionAgent reflects scene emotion.
- PromptAssembler adds compact scene narrative and scene rules.
## Sprint26: Provider Prompt Adapter

- Added `ProviderPromptAdapter`.
- Added `canonical_prompt` to PromptAssembler output.
- Added `provider_prompt_adapter` step to Planner and ExecutionEngine.
- Registered provider adapter in Orchestrator.
- FLUX provider prompt is now used as `final_prompt` for GenerationAgent.
- GPT Image and SDXL adapter skeletons were added.
## Sprint27: Provider Router

- Added `ProviderRouter`.
- Added `provider_router` step before `provider_prompt_adapter`.
- Orchestrator registers provider_router.
- ExecutionEngine stores `provider_routing` and `provider`.
- ProviderPromptAdapter now uses state-selected provider instead of hardcoded flux.
## Sprint29: Prompt Critic Agent

- Added `PromptCriticAgent`.
- Inserted `prompt_critic` after `prompt_assembler` and before provider routing.
- Prompt reports now include duplicate keywords, missing sections, warnings, quality score, and suggestions.
- The workflow falls back to `quality_score=100` if prompt critique fails.

## Sprint30A: Standard Agent Interface

- Added `ToolRegistry.run_with_state(name, state)`.
- Added state-based mode to ScenePlanningAgent, PromptAssembler, PromptCriticAgent, ProviderRouter, and ProviderPromptAdapter.
- ExecutionEngine now uses `state.update(result)` for selected upper-layer prompt and provider steps.
- Existing argument-based calls remain supported for backward compatibility.

## Sprint31: Prompt Optimizer Agent

- Added `PromptOptimizerAgent`.
- Inserted `prompt_optimizer` after `prompt_critic` and before provider routing.
- Optimized prompt now updates `optimized_prompt`, `canonical_prompt`, and `final_prompt`.
- ProviderPromptAdapter records `used optimized prompt` when optimizer output is present.

## Sprint32: Intelligent Prompt Optimizer

- PromptOptimizerAgent now reads `prompt_report` before editing.
- Added reasoning steps, before score, and estimated after score to `optimization_report`.
- Optimizer now reacts separately to duplicates, missing sections, warnings, and score bands.
- ExecutionEngine prints Prompt Preview before generation.
