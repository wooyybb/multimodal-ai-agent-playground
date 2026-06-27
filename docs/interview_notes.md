# Interview Notes

## Q: 이 프로젝트는 Multi-Agent인가요?

A: 네, 현재는 초기 multi-agent architecture 단계입니다. `OrchestratorAgent`가 전체 workflow를 조율하고, `VisionAgent`, `PromptAgent`, `GenerationAgent`가 각각 이미지 caption 생성, final prompt 생성, mock image generation을 담당합니다. 아직 모든 agent가 완성된 것은 아니지만, 단일 함수형 pipeline에서 agent 역할을 분리하는 방향으로 발전 중입니다.

## Q: OrchestratorAgent는 왜 필요한가요?

A: agent가 늘어나면 실행 순서, 입력과 출력 전달, trace 기록, retry loop, memory 저장 같은 조율 책임이 생깁니다. 이 책임을 `workflow/pipeline.py`에 계속 넣으면 pipeline이 비대해질 수 있습니다. `OrchestratorAgent`를 두면 pipeline은 실행 진입점(entry point) 역할을 하고, agent coordination은 orchestrator가 담당하게 됩니다.

## Q: Codex를 사용했는데 본인이 한 역할은 무엇인가요?

A: Codex는 코드 작성과 문서화 속도를 높이는 assistant로 활용했습니다. 저는 전체 아키텍처 방향, agent 역할 분리, mock-first 개발 전략, 단계별 sprint 계획을 설계하고, 생성된 코드가 요구사항과 프로젝트 목표에 맞는지 검토했습니다. 즉, 단순히 코드를 생성한 것이 아니라 시스템 설계 의도와 개발 순서를 정하고 결과물을 검증하는 역할을 했습니다.

## Q: 왜 실제 FLUX를 바로 붙이지 않고 mock GenerationAgent를 먼저 만들었나요?

A: 실제 FLUX를 바로 연결하면 API, GPU, dependency, 인증 정보 같은 외부 요인 때문에 구조 검증이 늦어질 수 있습니다. 먼저 mock `GenerationAgent`를 만들면 final prompt가 image generation 단계까지 제대로 전달되는지 확인할 수 있고, 출력 경로(`output_image_path`)를 포함한 pipeline contract도 안정적으로 정할 수 있습니다. 이후 실제 FLUX는 `FluxTool` 내부 구현만 교체하는 방식으로 연결할 수 있습니다.

## Q: 왜 CLIP 기반 EvaluationAgent가 필요한가요?

A: 이미지 생성 결과를 사람이 매번 주관적으로 확인하면 retry loop나 자동 개선 흐름을 만들기 어렵습니다. `EvaluationAgent`는 생성된 이미지와 reference image, final prompt 사이의 유사도(similarity)를 score로 제공하는 역할을 합니다. 현재는 mock score지만, 향후 실제 CLIP similarity, DINO similarity, aesthetic score로 확장하면 자동 평가와 개선 루프의 기준점이 됩니다.

## Q: EvaluationAgent를 PromptAgent나 GenerationAgent 안에 넣지 않은 이유는 무엇인가요?

A: `PromptAgent`는 prompt 생성, `GenerationAgent`는 image generation, `EvaluationAgent`는 result evaluation이라는 서로 다른 책임을 가집니다. 평가 로직을 다른 agent 안에 넣으면 역할이 섞이고 추후 평가 기준을 바꾸기 어려워집니다. 별도 agent로 분리하면 평가 방식만 독립적으로 교체하거나 확장할 수 있고, score를 `ReflectionAgent`와 `RetryAgent`에 명확히 전달할 수 있습니다.

## Q: ReflectionAgent는 왜 필요한가요?

A: `EvaluationAgent`가 score를 제공해도, score만으로는 무엇을 개선해야 하는지 알기 어렵습니다. `ReflectionAgent`는 평가 결과를 바탕으로 실패 원인을 분석하고, 다음 generation에 사용할 수 있는 `suggested_prompt`를 제안하는 역할을 합니다. 현재는 rule-based mock이지만, 향후 LLM 기반 reflection으로 확장할 수 있습니다.

## Q: Retry threshold는 왜 필요한가요?

A: retry 여부를 일관되게 판단하려면 기준점이 필요합니다. 현재는 `0.75`를 threshold로 두고, score가 이보다 낮으면 retry 후보로 표시합니다. 실제 재생성 loop는 아직 실행하지 않지만, 이 값은 feedback loop를 설계하기 위한 첫 번째 decision boundary입니다.

## Q: 현재 Reflection은 실제 LLM인가요?

A: 아닙니다. 현재 `ReflectionAgent`는 실제 LLM API를 호출하지 않는 rule-based mock reflection입니다. score가 낮으면 정해진 규칙에 따라 개선 제안과 suggested prompt를 반환하고, score가 충분하면 `"no major revision needed"`를 반환합니다.
