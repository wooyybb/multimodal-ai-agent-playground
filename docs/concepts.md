# Concepts

## Evaluation Agent

`EvaluationAgent`는 생성 결과를 정량적으로 평가하는 agent입니다. Multi-agent workflow에서 generation 이후 단계에 위치하며, 생성된 이미지가 reference image와 final prompt에 얼마나 잘 맞는지 score로 표현합니다.

현재 버전에서는 실제 CLIP 모델을 로드하지 않고 mock score를 반환합니다. 이 mock score는 generated image file 존재 여부와 prompt 길이를 활용해 deterministic하게 계산됩니다.

향후에는 다음 평가 방식으로 확장할 수 있습니다.

- CLIP similarity: reference image, generated image, prompt 간 semantic similarity 평가
- DINO similarity: 이미지 간 visual feature similarity 평가
- Aesthetic score: 생성 이미지의 미적 품질 평가

이 score는 이후 `ReflectionAgent`가 prompt 개선 제안을 만들고, `RetryAgent`가 재시도 여부를 판단하는 feedback loop의 핵심 입력으로 사용할 수 있습니다.
