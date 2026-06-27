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
