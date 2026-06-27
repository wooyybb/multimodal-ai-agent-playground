# Design Decisions

## 왜 Reflection을 Agent로 분리했는가

`ReflectionAgent`는 평가 결과를 해석하고 개선 방향을 제안하는 feedback agent입니다. 이 책임을 `EvaluationAgent`나 `PromptAgent`에 넣으면 평가, 분석, prompt 생성의 책임이 섞입니다.

별도 agent로 분리하면 현재 rule-based mock reflection을 유지하면서도, 향후 LLM 기반 reflection으로 자연스럽게 교체할 수 있습니다.

## 왜 RetryAgent를 따로 만들었는가

`RetryAgent`는 score가 threshold를 넘는지 판단하는 decision agent입니다. Reflection은 "무엇을 개선할지"를 말하고, Retry는 "다시 시도할지"를 결정합니다.

이 둘을 분리하면 나중에 retry 정책을 score threshold, 사용자 선호, 비용 제한, memory history 기반 정책으로 확장할 수 있습니다.

## 왜 Memory를 Sprint 7에 붙였는가

Self-improving AI Agent는 이전 실행 결과를 기억해야 개선 방향을 학습할 수 있습니다. 현재는 단순히 `history.json`에 저장하지만, 이 기록은 향후 prompt 개선, retry 분석, 성능 비교의 기반이 됩니다.

## 왜 MemoryManager를 도입했는가

초기 `History` 클래스는 저장(save)에 집중한 단순 유틸이었습니다. Sprint 7 Memory Engineering에서는 memory를 agent context와 state management의 interface로 다루기 위해 `MemoryManager`를 도입했습니다.

`MemoryManager`는 `load_last_run()`, `save_run()`, `get_history()`, `clear_history()`를 제공해 orchestrator가 memory를 일관된 방식으로 사용할 수 있게 합니다.

## 왜 Memory는 Agent가 아니고 Manager인가

현재 memory는 판단하거나 생성하는 agent가 아니라 상태(state)를 저장하고 조회하는 infrastructure layer입니다. 따라서 `MemoryAgent`보다 `MemoryManager`라는 이름이 역할을 더 정확히 드러냅니다.

향후 memory retrieval, summarization, preference learning처럼 능동적 판단이 들어가면 별도 Memory Agent를 검토할 수 있습니다.

## 왜 Orchestrator만 Memory에 접근하게 했는가

개별 agent가 memory file이나 database에 직접 접근하면 agent 간 결합도가 높아집니다. `VisionAgent`, `PromptAgent`, `EvaluationAgent`는 자신의 전문 작업에만 집중하고, state load/save는 `OrchestratorAgent`가 담당하도록 했습니다.

이 구조는 loose coupling을 유지합니다. 향후 JSON에서 SQLite 또는 vector DB로 바뀌어도 대부분의 agent 코드는 변경하지 않아도 됩니다.

## 왜 무한 Retry가 아니라 1회 Retry로 시작했는가

초기 MVP에서는 debug 가능성과 안정성이 중요합니다. 무한 retry는 종료 조건, 비용, 실행 시간, memory schema를 복잡하게 만듭니다.

1회 retry는 reflection 기반 개선이 실제 workflow에 반영되는지 검증하기에 충분하면서도, loop가 폭주하지 않도록 제어할 수 있습니다.

## 왜 Orchestrator가 Retry Loop를 제어하는가

`RetryAgent`는 정책 판단(policy decision)을 담당하고, `OrchestratorAgent`는 workflow state transition을 담당합니다. retry 실행까지 `RetryAgent`가 맡으면 agent 책임이 섞입니다.

따라서 `RetryAgent.should_retry(score)`는 bool만 반환하고, second generation과 evaluation 실행은 orchestrator가 제어합니다.

## 왜 Best Result를 저장하는가

initial attempt와 retry attempt가 모두 존재할 때는 최종적으로 어떤 결과를 사용할지 명확해야 합니다. `best_score`, `best_prompt`, `best_output_image_path`를 저장하면 이후 UI, memory analysis, portfolio 설명에서 최종 선택 기준을 추적할 수 있습니다.

## 왜 UI가 Agent를 직접 호출하지 않고 Pipeline을 호출하는가

UI가 개별 agent를 직접 호출하면 화면 코드가 workflow 순서와 retry policy를 알게 됩니다. 그러면 agent 구조가 바뀔 때 UI도 함께 수정해야 합니다.

`ui/app.py`는 `MultimodalPipeline`만 호출하고, pipeline은 `OrchestratorAgent`를 호출합니다. 이 구조는 UI를 result visualization layer로 유지하고, agent orchestration은 backend workflow에 남겨 둡니다.

## 왜 모델 통합 전에 UI를 먼저 연결하는가

실제 BLIP, FLUX, CLIP을 붙이기 전에도 사용자가 workflow를 실행하고 결과 trace를 확인할 수 있어야 합니다. Gradio UI를 먼저 연결하면 demo-driven development가 가능해지고, 이후 실제 모델을 붙였을 때 사용자 흐름을 다시 설계하지 않아도 됩니다.

## 왜 BLIP를 VisionAgent 내부가 아니라 BlipTool로 분리했는가

`VisionAgent`는 image captioning이라는 agent responsibility만 가져야 합니다. model loading, processor, torch inference, image preprocessing은 implementation detail입니다.

이를 `BlipTool`로 분리하면 VisionAgent interface를 유지하면서 BLIP, BLIP-2, LLaVA, external VLM API 등으로 tool implementation을 교체할 수 있습니다.

## 왜 Lazy Loading을 사용하는가

BLIP 모델은 무겁고 로딩 시간이 있습니다. 앱 시작이나 import 시점마다 모델을 로딩하면 UI 실행이 느려지고 테스트도 어려워집니다.

lazy loading을 사용하면 첫 caption 요청 시점에만 model과 processor를 로드하고, 이후에는 재사용할 수 있습니다.

## 왜 Fallback Caption이 필요한가

실제 모델 통합은 dependency, network, model cache, device 문제로 실패할 수 있습니다. fallback caption을 두면 BLIP 실패가 전체 multi-agent workflow 중단으로 이어지지 않습니다.

현재 fallback caption은 `"An uploaded image"`입니다.
