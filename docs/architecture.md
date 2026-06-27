# Architecture

이 프로젝트는 단일 파이프라인(Single Pipeline)에서 멀티 에이전트 아키텍처(Multi-Agent Architecture)로 발전 중입니다.

## Current Structure

```text
User -> OrchestratorAgent -> VisionAgent -> PromptAgent -> GenerationAgent -> EvaluationAgent -> ReflectionAgent -> RetryAgent -> Memory
```

현재 버전은 사용자의 이미지 입력과 텍스트 요청을 받아 `OrchestratorAgent`가 전체 workflow를 조율합니다. `VisionAgent`는 이미지를 caption으로 변환하고, `PromptAgent`는 caption과 user prompt를 조합해 final prompt를 생성합니다. 이후 `GenerationAgent`가 final prompt를 받아 PIL 기반 mock image를 생성하고, `EvaluationAgent`가 mock CLIP similarity score를 반환합니다. `ReflectionAgent`는 평가 결과를 분석해 suggested prompt를 만들고, `RetryAgent`는 threshold 기반으로 retry 여부를 판단합니다. 마지막으로 `Memory`가 실행 기록을 `history.json`에 저장합니다.

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
- `Memory`: caption, prompt, score, reflection, retry, timestamp를 `memory/history.json`에 저장합니다.
