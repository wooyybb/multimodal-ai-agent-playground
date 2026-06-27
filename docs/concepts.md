# Concepts

## Evaluation Agent

`EvaluationAgent`는 생성 결과를 정량적으로 평가하는 agent입니다. Multi-agent workflow에서 generation 이후 단계에 위치하며, 생성된 이미지가 reference image와 final prompt에 얼마나 잘 맞는지 score로 표현합니다.

현재 버전에서는 실제 CLIP 모델을 로드하지 않고 mock score를 반환합니다. 이 mock score는 generated image file 존재 여부와 prompt 길이를 활용해 deterministic하게 계산됩니다.

향후에는 다음 평가 방식으로 확장할 수 있습니다.

- CLIP similarity: reference image, generated image, prompt 간 semantic similarity 평가
- DINO similarity: 이미지 간 visual feature similarity 평가
- Aesthetic score: 생성 이미지의 미적 품질 평가

이 score는 이후 `ReflectionAgent`가 prompt 개선 제안을 만들고, `RetryAgent`가 재시도 여부를 판단하는 feedback loop의 핵심 입력으로 사용할 수 있습니다.

## Reflection Agent

`ReflectionAgent`는 평가 결과를 바탕으로 실패 원인을 분석하는 agent입니다. Multi-agent workflow에서 evaluation 이후 단계에 위치하며, score가 낮을 때 어떤 방향으로 prompt를 개선해야 하는지 제안합니다.

현재 버전은 rule-based mock reflection입니다. 실제 LLM API를 호출하지 않고, score가 `0.75` 미만이면 개선 문구와 `suggested_prompt`를 반환합니다. score가 `0.75` 이상이면 `"no major revision needed"`를 반환합니다.

향후에는 LLM 기반 reflection으로 확장할 수 있습니다. 예를 들어 generated image, reference image caption, final prompt, evaluation score, memory history를 함께 입력해 더 구체적인 실패 원인과 개선 prompt를 생성할 수 있습니다.

## Retry

`RetryAgent`는 retry decision을 담당하는 agent입니다. 현재는 threshold `0.75`를 기준으로 score가 낮으면 retry가 필요하다고 판단합니다.

이번 Sprint에서는 실제 재생성 loop를 실행하지 않습니다. 대신 `retry_needed` 값을 반환해 다음 Sprint에서 retry loop를 연결할 수 있는 구조를 만듭니다.

## Memory

`Memory`는 agent workflow의 실행 기록을 저장하는 layer입니다. 현재는 `memory/history.json`에 JSON 형태로 기록합니다.

저장 항목은 `caption`, `prompt`, `score`, `reflection`, `retry`, `timestamp`입니다. 향후에는 이 기록을 분석해 prompt 개선, retry 정책, agent 성능 비교에 활용할 수 있습니다.
