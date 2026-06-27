# Design Decisions

## 왜 Reflection을 Agent로 분리했는가

`ReflectionAgent`는 평가 결과를 해석하고 개선 방향을 제안하는 feedback agent입니다. 이 책임을 `EvaluationAgent`나 `PromptAgent`에 넣으면 평가, 분석, prompt 생성의 책임이 섞입니다.

별도 agent로 분리하면 현재 rule-based mock reflection을 유지하면서도, 향후 LLM 기반 reflection으로 자연스럽게 교체할 수 있습니다.

## 왜 RetryAgent를 따로 만들었는가

`RetryAgent`는 score가 threshold를 넘는지 판단하는 decision agent입니다. Reflection은 "무엇을 개선할지"를 말하고, Retry는 "다시 시도할지"를 결정합니다.

이 둘을 분리하면 나중에 retry 정책을 score threshold, 사용자 선호, 비용 제한, memory history 기반 정책으로 확장할 수 있습니다.

## 왜 Memory를 Sprint 7에 붙였는가

Self-improving AI Agent는 이전 실행 결과를 기억해야 개선 방향을 학습할 수 있습니다. 현재는 단순히 `history.json`에 저장하지만, 이 기록은 향후 prompt 개선, retry 분석, 성능 비교의 기반이 됩니다.
