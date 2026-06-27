# Architecture

이 프로젝트는 단일 파이프라인(Single Pipeline)에서 멀티 에이전트 아키텍처(Multi-Agent Architecture)로 발전 중입니다.

## Current Structure

```text
User -> OrchestratorAgent
├── MemoryManager(load)
├── VisionAgent
├── PromptAgent
├── GenerationAgent
├── EvaluationAgent
├── ReflectionAgent
├── RetryAgent
└── MemoryManager(save)
```

현재 버전은 사용자의 이미지 입력과 텍스트 요청을 받아 `OrchestratorAgent`가 전체 workflow를 조율합니다. 시작 시 `MemoryManager`가 마지막 실행 기록을 load하고, 이후 `VisionAgent`, `PromptAgent`, `GenerationAgent`, `EvaluationAgent`, `ReflectionAgent`, `RetryAgent`가 순서대로 실행됩니다. 마지막으로 `MemoryManager`가 현재 실행 기록을 `memory/history.json`에 save합니다. Memory 접근은 `OrchestratorAgent`로 제한해 개별 agent가 저장소 구조에 직접 의존하지 않도록 설계했습니다.

## Future Structure

```text
User -> OrchestratorAgent -> VisionAgent -> PromptAgent -> GenerationAgent -> EvaluationAgent -> ReflectionAgent -> RetryAgent -> Memory
```

향후 버전에서는 실제 재생성 loop와 LLM 기반 reflection을 연결할 예정입니다.

## Agent Roles

- `OrchestratorAgent`: 전체 multi-agent workflow를 조율하는 중앙 조정자(coordinator)입니다.
- `VisionAgent`: 이미지에서 caption을 추출하는 vision 담당 agent입니다. 현재는 mock BLIP tool을 사용합니다.
- `PromptAgent`: caption과 user prompt를 조합해 image generation용 final prompt를 생성합니다.
- `GenerationAgent`: final prompt를 기반으로 mock image를 생성합니다. 현재는 실제 FLUX가 아니라 PIL을 사용합니다.
- `EvaluationAgent`: 생성된 이미지와 prompt의 품질을 평가합니다. 현재는 실제 CLIP이 아니라 deterministic mock score를 반환합니다.
- `ReflectionAgent`: 평가 score와 prompt를 바탕으로 개선 제안과 suggested prompt를 생성합니다. 현재는 rule-based mock reflection입니다.
- `RetryAgent`: 평가 score가 threshold보다 낮은지 판단해 retry 여부를 반환합니다. 아직 실제 재생성 loop는 실행하지 않습니다.
- `MemoryManager`: working memory와 episodic memory의 시작점입니다. `load_last_run()`, `save_run()`, `get_history()`, `clear_history()` interface를 제공합니다.

## One-Step Retry Loop

Sprint 8에서는 one-step retry loop를 추가했습니다. `EvaluationAgent`가 initial score를 만들고, `ReflectionAgent`가 suggested prompt를 제안한 뒤, `RetryAgent`가 retry 여부를 판단합니다.

```text
GenerationAgent(initial_prompt)
-> EvaluationAgent(initial_score)
-> ReflectionAgent(suggested_prompt)
-> RetryAgent(should_retry)
-> if retry_needed:
     GenerationAgent(suggested_prompt)
     EvaluationAgent(retry_score)
-> best result selection
-> MemoryManager(save)
```

무한 반복을 피하기 위해 retry는 최대 1회만 수행합니다. `OrchestratorAgent`가 loop를 제어하고, `RetryAgent`는 `should_retry(score)` 판단만 담당합니다.

## Gradio UI Integration

Sprint 9에서는 Gradio UI를 `MultimodalPipeline`에 연결했습니다. UI는 agent를 직접 호출하지 않고 pipeline만 호출합니다.

```text
User
-> Gradio UI
-> MultimodalPipeline
-> OrchestratorAgent
-> VisionAgent
-> PromptAgent
-> GenerationAgent
-> EvaluationAgent
-> ReflectionAgent
-> RetryAgent
-> MemoryManager
-> Gradio UI Output
```

이 구조는 UI와 agent workflow 책임을 분리합니다. UI는 image input, user prompt, result visualization, agent trace display에 집중하고, 실행 순서와 retry loop는 `OrchestratorAgent`가 관리합니다.

## Real BLIP Captioning

Sprint 10에서는 mock caption을 실제 BLIP 기반 image captioning으로 교체했습니다.

```text
VisionAgent
-> BlipTool
-> Salesforce/blip-image-captioning-base
-> Real BLIP Caption
```

`VisionAgent`는 model loading이나 inference details를 알지 않습니다. 실제 BLIP processor/model loading, PIL image 변환, torch inference, fallback caption 처리는 `BlipTool`이 담당합니다.

## Real FLUX Generation

Sprint 11에서는 `GenerationAgent`가 `FluxTool`을 통해 real FLUX generation을 시도하도록 확장했습니다.

```text
PromptAgent
-> GenerationAgent
-> FluxTool
   -> Real FLUX generation if HF_TOKEN exists
   -> Mock fallback image if token is missing or generation fails
```

`GenerationAgent`는 Hugging Face API details를 알지 않습니다. `FluxTool`이 `HF_TOKEN`, `InferenceClient`, image saving, fallback generation을 담당합니다.

## Real CLIP Evaluation

Sprint 12에서는 mock score를 실제 CLIP 기반 image-text similarity score로 확장했습니다.

```text
GenerationAgent
-> EvaluationAgent
-> ClipTool
-> openai/clip-vit-base-patch32
-> image-text similarity score
```

`EvaluationAgent`는 CLIP model internals를 알지 않습니다. `ClipTool`이 processor/model lazy loading, generated image loading, text embedding, image embedding, cosine similarity calculation, fallback score를 담당합니다.
