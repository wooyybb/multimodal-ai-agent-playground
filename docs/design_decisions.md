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

## 왜 FLUX를 GenerationAgent 내부가 아니라 FluxTool로 분리했는가

`GenerationAgent`는 prompt를 받아 image path를 반환하는 agent interface에 집중해야 합니다. Hugging Face token, API client, image saving, fallback image 생성은 tool implementation detail입니다.

`FluxTool`로 분리하면 이후 local diffusers, SDXL, 다른 image generation API로 교체해도 `GenerationAgent` interface를 유지할 수 있습니다.

## 왜 API 기반으로 먼저 통합했는가

FLUX를 local inference로 실행하려면 GPU, VRAM, diffusers 설정, 모델 다운로드 부담이 큽니다. MVP 단계에서는 Hugging Face Inference API 기반 통합이 빠르고 local hardware 의존성을 줄일 수 있습니다.

## 왜 Fallback Mock Generation을 유지하는가

실제 image generation API는 token, network, quota, service 상태에 따라 실패할 수 있습니다. fallback image를 유지하면 generation 실패가 전체 multi-agent workflow 중단으로 이어지지 않습니다.

## 왜 HF_TOKEN을 환경변수로 사용하는가

API token은 보안 정보이므로 코드에 직접 넣으면 안 됩니다. `HF_TOKEN` 환경변수를 사용하면 local 개발, 배포, demo 환경에서 token을 분리해 관리할 수 있습니다.

## 왜 CLIP을 EvaluationAgent 내부가 아니라 ClipTool로 분리했는가

`EvaluationAgent`는 evaluation 단계의 agent 역할만 담당해야 합니다. CLIP processor, model loading, embedding extraction, cosine similarity 계산은 tool implementation detail입니다.

`ClipTool`로 분리하면 향후 DINO similarity, aesthetic score, human preference model 등으로 평가 backend를 교체하기 쉽습니다.

## 왜 Image-Text Similarity부터 시작했는가

현재 pipeline의 핵심 출력은 generated image와 final prompt입니다. 따라서 먼저 image와 text가 얼마나 잘 맞는지 평가하는 것이 가장 직접적입니다.

reference image similarity는 중요한 확장 포인트지만, 이번 Sprint에서는 interface만 유지하고 generated image와 final prompt의 alignment를 먼저 평가합니다.

## 왜 Reference Image Interface를 유지하는가

`EvaluationAgent.run(reference_image, generated_image_path, final_prompt)` interface를 유지하면 향후 image-image similarity나 reference-guided evaluation을 추가할 때 orchestrator 변경을 줄일 수 있습니다.

이번 Sprint에서는 reference image를 사용하지 않지만, 다음 평가 확장을 위한 compatibility를 남겨 둡니다.

## 왜 Fallback Score를 0.0으로 두는가

CLIP loading 또는 inference 실패는 평가를 신뢰할 수 없다는 의미입니다. 이 경우 높은 점수를 주면 retry loop가 잘못된 판단을 할 수 있으므로 `0.0`을 반환합니다.

## 왜 기능 추가 대신 Integration Test Sprint를 진행했는가

BLIP, FLUX, CLIP, Reflection, Retry, Memory, UI가 모두 연결된 뒤에는 새 기능보다 End-to-End 안정성이 더 중요합니다. 검증 없이 기능만 추가하면 portfolio demo에서 실제 흐름을 설명하기 어려워집니다.

Sprint 13은 전체 workflow가 이미지 입력부터 UI 출력과 memory 저장까지 이어지는지 확인하기 위한 안정화 Sprint입니다.

## 왜 Demo Script와 Known Issues를 문서화했는가

면접이나 portfolio demo에서는 완벽한 시스템보다 현재 가능한 것과 한계를 명확히 설명하는 능력이 중요합니다. `demo_script.md`는 시연 흐름을 정리하고, `known_issues.md`는 모델/API/fallback의 한계를 투명하게 기록합니다.

## 왜 LLM Planner가 아니라 Rule-based Planner로 시작했는가

Planner 개념을 처음 도입하는 단계에서는 예측 가능성과 디버깅 가능성이 중요합니다. Rule-based planner는 입력 조건과 execution plan이 명확해 학습과 검증에 적합합니다.

향후에는 LLM-based planning으로 확장할 수 있지만, 먼저 Planner와 Orchestrator의 책임 분리를 안정화하는 것이 우선입니다.

## 왜 PlannerAgent가 직접 실행하지 않고 계획만 생성하는가

PlannerAgent는 "무엇을 할지"를 계획하고, OrchestratorAgent는 "어떻게 실행할지"를 관리합니다. Planner가 직접 agent를 실행하면 planning과 orchestration 책임이 섞입니다.

따라서 이번 Sprint에서는 PlannerAgent가 execution plan만 만들고, OrchestratorAgent가 기존 workflow를 그대로 실행합니다.

## 왜 이번 Sprint에서 Dynamic Execution Engine까지 구현하지 않았는가

동적 실행 엔진은 conditional branch, skipped step, dependency management, failure handling을 함께 설계해야 합니다. 한 번에 도입하면 기존 E2E 안정성이 흔들릴 수 있습니다.

이번 Sprint는 plan 생성과 기록을 먼저 도입하고, 다음 단계에서 execution plan 기반 동적 실행으로 확장할 수 있게 준비하는 단계입니다.

## 왜 Orchestrator가 Agent를 직접 호출하지 않고 ToolRegistry를 사용하게 했는가

Agent와 Tool이 늘어날수록 Orchestrator가 모든 구현 객체를 직접 알고 호출하는 구조는 결합도가 높아집니다. `ToolRegistry`를 두면 Orchestrator는 이름 기반 호출을 사용하고, 실제 callable 관리 책임은 Registry가 담당합니다.

이 구조는 Dependency Inversion과 Open-Closed Principle을 학습하기에 적합합니다. 새 tool을 추가할 때 Orchestrator 내부 로직을 크게 바꾸지 않고 registry 등록을 확장할 수 있습니다.

## 왜 이번 Sprint에서 완전한 Dynamic Execution Engine까지 구현하지 않았는가

Planner의 execution plan을 for-loop로 실행하는 dynamic engine은 branch, skipped step, argument passing, error recovery를 함께 다뤄야 합니다. 이번 Sprint에서는 기존 E2E 안정성을 유지하면서 registry 기반 호출 구조만 도입했습니다.

## 왜 Tool 이름을 Planner execution_plan과 맞췄는가

Planner가 생성한 plan step과 Registry에 등록된 tool name이 같아야 향후 dynamic execution engine으로 자연스럽게 확장할 수 있습니다. 이번 Sprint에서는 `memory_load`, `vision`, `prompt`, `generation`, `evaluation`, `reflection`, `retry`, `memory_save` 이름을 맞췄습니다.
