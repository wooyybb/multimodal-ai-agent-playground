# Architecture

이 프로젝트는 단일 파이프라인(Single Pipeline)에서 멀티 에이전트 아키텍처(Multi-Agent Architecture)로 발전 중입니다.

## Current Structure

```text
User -> OrchestratorAgent -> VisionAgent -> PromptAgent
```

현재 버전은 사용자의 이미지 입력과 텍스트 요청을 받아 `OrchestratorAgent`가 전체 흐름을 조율합니다. `VisionAgent`는 이미지를 caption으로 변환하고, `PromptAgent`는 caption과 user prompt를 조합해 final prompt를 생성합니다.

## Future Structure

```text
User -> OrchestratorAgent -> VisionAgent -> PromptAgent -> GenerationAgent -> EvaluationAgent -> ReflectionAgent -> Memory
```

향후 버전에서는 이미지 생성(Generation), 평가(Evaluation), 개선 제안(Reflection), 재시도(Retry), 기록 저장(Memory)까지 연결할 예정입니다.

## Agent Roles

- `OrchestratorAgent`: 전체 multi-agent workflow를 조율하는 중앙 조정자(coordinator)입니다.
- `VisionAgent`: 이미지에서 caption을 추출하는 vision 담당 agent입니다. 현재는 mock BLIP tool을 사용합니다.
- `PromptAgent`: caption과 user prompt를 조합해 image generation용 final prompt를 생성합니다.
- `GenerationAgent`: final prompt를 기반으로 이미지를 생성할 예정입니다. 현재는 skeleton 상태입니다.
- `EvaluationAgent`: 생성된 이미지와 prompt의 품질을 평가할 예정입니다. 현재는 skeleton 상태입니다.
- `ReflectionAgent`: 평가 score와 prompt를 바탕으로 개선 제안을 생성합니다. 현재는 mock 응답을 반환합니다.
- `RetryAgent`: 평가 결과가 낮을 때 prompt 개선과 재생성을 반복하는 retry loop를 담당할 예정입니다.
- `Memory`: 실행 기록, prompt, 평가 결과를 저장하는 memory layer로 확장할 예정입니다.
