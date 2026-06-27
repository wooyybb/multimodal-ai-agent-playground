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
