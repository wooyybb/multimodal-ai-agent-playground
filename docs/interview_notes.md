# Interview Notes

## Q: 이 프로젝트는 Multi-Agent인가요?

A: 네, 현재는 초기 multi-agent architecture 단계입니다. `OrchestratorAgent`가 전체 workflow를 조율하고, `VisionAgent`, `PromptAgent`, `GenerationAgent`가 각각 이미지 caption 생성, final prompt 생성, mock image generation을 담당합니다. 아직 모든 agent가 완성된 것은 아니지만, 단일 함수형 pipeline에서 agent 역할을 분리하는 방향으로 발전 중입니다.

## Q: OrchestratorAgent는 왜 필요한가요?

A: agent가 늘어나면 실행 순서, 입력과 출력 전달, trace 기록, retry loop, memory 저장 같은 조율 책임이 생깁니다. 이 책임을 `workflow/pipeline.py`에 계속 넣으면 pipeline이 비대해질 수 있습니다. `OrchestratorAgent`를 두면 pipeline은 실행 진입점(entry point) 역할을 하고, agent coordination은 orchestrator가 담당하게 됩니다.

## Q: Codex를 사용했는데 본인이 한 역할은 무엇인가요?

A: Codex는 코드 작성과 문서화 속도를 높이는 assistant로 활용했습니다. 저는 전체 아키텍처 방향, agent 역할 분리, mock-first 개발 전략, 단계별 sprint 계획을 설계하고, 생성된 코드가 요구사항과 프로젝트 목표에 맞는지 검토했습니다. 즉, 단순히 코드를 생성한 것이 아니라 시스템 설계 의도와 개발 순서를 정하고 결과물을 검증하는 역할을 했습니다.

## Q: 왜 실제 FLUX를 바로 붙이지 않고 mock GenerationAgent를 먼저 만들었나요?

A: 실제 FLUX를 바로 연결하면 API, GPU, dependency, 인증 정보 같은 외부 요인 때문에 구조 검증이 늦어질 수 있습니다. 먼저 mock `GenerationAgent`를 만들면 final prompt가 image generation 단계까지 제대로 전달되는지 확인할 수 있고, 출력 경로(`output_image_path`)를 포함한 pipeline contract도 안정적으로 정할 수 있습니다. 이후 실제 FLUX는 `FluxTool` 내부 구현만 교체하는 방식으로 연결할 수 있습니다.
