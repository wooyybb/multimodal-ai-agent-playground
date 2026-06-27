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

## Q: Reflection이란?

A: Reflection은 agent가 자신의 결과를 평가하고, 다음 시도에서 무엇을 개선해야 할지 분석하는 과정입니다. 이 프로젝트에서는 `EvaluationAgent`의 score를 바탕으로 `ReflectionAgent`가 개선 설명과 `suggested_prompt`를 생성합니다.

## Q: 왜 RetryAgent가 필요한가?

A: Reflection이 개선 방향을 제안하더라도, 언제 다시 시도할지 판단하는 decision boundary가 필요합니다. `RetryAgent`는 threshold 기반으로 retry 여부를 결정해 orchestration 흐름을 명확하게 만듭니다.

## Q: 왜 Memory를 붙였는가?

A: Self-improving agent는 이전 실행의 caption, prompt, score, reflection, retry 여부를 기억해야 다음 개선에 활용할 수 있습니다. 현재는 `history.json` 저장으로 시작하고, 이후 검색 가능한 memory나 통계 분석으로 확장할 수 있습니다.

## Q: Codex를 어떻게 활용했는가?

A: Codex는 sprint 요구사항을 코드와 문서로 빠르게 반영하는 pair engineer로 활용했습니다. 저는 architecture 목표, allowed files, forbidden files, done definition을 명확히 제시했고, Codex는 그 제약 안에서 구현과 검증을 수행했습니다.

## Q: Prompt Engineering은 어떻게 했는가?

A: 이번 prompt는 단순 구현 지시가 아니라 Architecture Prompt로 작성했습니다. Task, Architecture, Workspace, Allowed Files, Forbidden Files, Requirements, Documentation, Done Definition 순서로 구성해 구현 범위와 검증 기준을 명확히 했습니다.

## Q: Memory와 Database의 차이는?

A: Memory는 agent가 이전 context를 활용하기 위한 설계 개념이고, Database는 그 memory를 저장하는 구현 수단입니다. 현재 프로젝트에서는 JSON 파일을 database처럼 사용하지만, 핵심은 agent가 과거 실행을 다시 읽을 수 있는 memory interface를 갖는 것입니다.

## Q: 왜 JSON으로 시작했나요?

A: 초기 단계에서는 복잡한 database보다 파일 기반 JSON이 구조를 검증하기 쉽습니다. schema를 눈으로 확인할 수 있고, dependency가 없으며, portfolio 설명에도 memory record가 명확히 드러납니다.

## Q: Memory는 왜 Agent가 아니고 Manager인가요?

A: 현재 memory는 독립적으로 판단하거나 생성하지 않고, 실행 기록을 load/save하는 상태 관리 layer입니다. 그래서 `MemoryManager`가 더 정확합니다. 나중에 검색, 요약, 선호도 추론이 들어가면 Memory Agent로 확장할 수 있습니다.

## Q: Working Memory와 Episodic Memory 차이는?

A: Working Memory는 현재 실행 중 임시로 유지되는 context이고, Episodic Memory는 과거 실행 episode를 저장한 장기 기록입니다. 이 프로젝트에서는 orchestrator 내부의 실행 state가 working memory이고, `history.json`의 run records가 episodic memory입니다.

## Q: Retry Loop는 왜 필요한가요?

A: 평가만 하고 끝나면 agent가 결과를 개선하는 행동을 하지 못합니다. Retry Loop는 낮은 score가 나왔을 때 reflection의 suggested prompt를 사용해 한 번 더 generation과 evaluation을 수행하게 해 self-improving 구조를 만듭니다.

## Q: 왜 1회 Retry로 제한했나요?

A: MVP 단계에서는 무한 loop를 피하고 debug 가능성을 높이는 것이 중요합니다. 1회 retry는 reflection 기반 개선 흐름을 검증하기에 충분하고, 실행 시간과 memory schema도 단순하게 유지할 수 있습니다.

## Q: RetryAgent가 직접 재생성을 수행하지 않는 이유는 무엇인가요?

A: `RetryAgent`는 retry 여부를 판단하는 policy agent입니다. 실제 generation과 evaluation 실행은 workflow state를 관리하는 `OrchestratorAgent`가 담당해야 agent 책임이 분리됩니다.

## Q: best_score를 저장하는 이유는 무엇인가요?

A: initial attempt와 retry attempt가 모두 있을 때 최종적으로 어떤 결과를 선택했는지 추적해야 합니다. `best_score`를 저장하면 성능 비교, UI 표시, memory 기반 분석에 사용할 수 있습니다.
