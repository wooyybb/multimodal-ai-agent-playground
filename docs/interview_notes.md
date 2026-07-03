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

## Q: 왜 Gradio UI를 먼저 연결했나요?

A: 실제 모델을 붙이기 전에도 사용자가 image와 prompt를 입력하고 전체 agent workflow를 확인할 수 있어야 합니다. Gradio UI는 빠르게 demo를 만들 수 있고, image input과 output visualization에 적합합니다.

## Q: UI가 직접 Agent를 호출하지 않고 Pipeline을 호출하는 이유는 무엇인가요?

A: UI가 agent 순서를 알면 orchestration 책임이 UI로 새어 나갑니다. UI는 `MultimodalPipeline`만 호출하고, agent 실행 순서는 `OrchestratorAgent`가 관리하게 해야 책임 분리가 유지됩니다.

## Q: Agent Trace를 UI에 보여주는 이유는 무엇인가요?

A: Multi-agent system은 결과뿐 아니라 어떤 agent들이 어떤 순서로 실행됐는지가 중요합니다. Agent trace를 보여주면 workflow가 실제로 Vision, Prompt, Generation, Evaluation, Reflection, Retry, Memory 단계를 거쳤는지 설명할 수 있습니다.

## Q: BLIP는 어떤 역할을 하나요?

A: BLIP는 이미지에서 자연어 caption을 생성하는 Vision-Language Model입니다. 이 프로젝트에서는 사용자가 업로드한 이미지를 `VisionAgent`가 이해할 수 있는 caption으로 변환하는 역할을 합니다.

## Q: VisionAgent와 BlipTool을 분리한 이유는 무엇인가요?

A: `VisionAgent`는 caption 생성이라는 agent 역할만 담당하고, 실제 모델 로딩과 inference는 `BlipTool`이 담당합니다. 이렇게 분리하면 나중에 BLIP-2, LLaVA, GPT-4o Vision 같은 다른 VLM으로 바꿔도 agent interface를 유지할 수 있습니다.

## Q: VLM Inference는 무엇인가요?

A: VLM Inference는 Vision-Language Model을 사용해 이미지와 언어 사이의 의미를 추론하는 과정입니다. 여기서는 BLIP가 이미지를 보고 caption을 생성하는 과정이 VLM inference입니다.

## Q: 왜 lazy loading을 사용하나요?

A: BLIP 모델은 로딩 비용이 크기 때문에 import나 앱 시작 시점에 바로 로딩하면 느려집니다. lazy loading을 사용하면 첫 caption 요청 시점에만 모델을 로드하고 이후에는 재사용할 수 있습니다.

## Q: BLIP가 실패하면 어떻게 처리하나요?

A: 모델 로딩이나 inference 중 오류가 발생하면 `BlipTool`은 fallback caption `"An uploaded image"`를 반환합니다. 이렇게 하면 vision 단계 실패가 전체 workflow 중단으로 이어지지 않습니다.

## Q: FLUX는 이 프로젝트에서 어떤 역할을 하나요?

A: FLUX는 final prompt를 기반으로 이미지를 생성하는 text-to-image generation 역할을 합니다. `GenerationAgent`는 `FluxTool`을 통해 FLUX generation을 요청하고, 생성된 image path를 downstream evaluation에 전달합니다.

## Q: GenerationAgent와 FluxTool을 분리한 이유는 무엇인가요?

A: `GenerationAgent`는 generation 단계의 agent 역할만 담당하고, Hugging Face API 호출, token 처리, fallback image 생성은 `FluxTool`이 담당합니다. 이렇게 하면 agent interface를 유지한 채 generation backend를 교체할 수 있습니다.

## Q: 실제 모델 연동 실패 시 어떻게 처리했나요?

A: Hugging Face token 환경변수가 없거나 API 호출이 실패하면 `FluxTool`이 PIL 기반 fallback mock image를 생성합니다. 따라서 외부 API 실패가 전체 workflow 중단으로 이어지지 않습니다.

## Q: 왜 환경변수로 Hugging Face token을 관리했나요?

A: Hugging Face token은 보안 정보이므로 코드나 문서에 직접 저장하면 안 됩니다. 환경변수로 관리하면 local 개발과 배포 환경에서 안전하게 분리할 수 있습니다.

## Q: mock fallback을 유지한 이유는 무엇인가요?

A: 실제 API는 network, quota, token 문제로 실패할 수 있습니다. fallback이 있으면 demo와 pipeline 검증을 계속할 수 있고, agent workflow의 안정성이 높아집니다.

## Q: CLIP은 이 프로젝트에서 어떤 역할을 하나요?

A: CLIP은 generated image와 final prompt가 의미적으로 얼마나 잘 맞는지 평가하는 model-based evaluator 역할을 합니다. EvaluationAgent가 ClipTool을 통해 score를 얻고, 이 score는 retry 판단과 reflection loop의 입력이 됩니다.

## Q: CLIP score는 무엇을 의미하나요?

A: CLIP score는 image embedding과 text embedding의 cosine similarity를 0.0~1.0 범위로 변환한 값입니다. 높을수록 생성 이미지가 prompt와 더 잘 맞는다고 해석할 수 있습니다.

## Q: 왜 EvaluationAgent와 ClipTool을 분리했나요?

A: EvaluationAgent는 평가 단계의 agent 책임만 가지고, 실제 CLIP model loading과 inference는 ClipTool이 담당합니다. 이렇게 분리하면 평가 backend를 바꿔도 agent interface를 유지할 수 있습니다.

## Q: reference_image를 이번 Sprint에서 사용하지 않는데 interface에 유지한 이유는 무엇인가요?

A: 향후 image-image similarity나 reference-guided evaluation을 추가하기 위해서입니다. 지금은 generated image와 final prompt의 image-text similarity만 계산하지만, interface를 유지하면 orchestrator 변경 없이 확장할 수 있습니다.

## Q: CLIP score만으로 생성 품질을 평가할 수 있나요?

A: CLIP score는 prompt alignment를 보는 데 유용하지만 이미지의 미적 품질, 디테일, 왜곡 여부까지 완벽히 평가하지는 못합니다. 향후 DINO similarity, aesthetic score, human preference evaluation과 함께 사용하는 것이 좋습니다.

## Q: End-to-End 테스트는 어떻게 했나요?

A: UI에서 image와 user prompt를 입력한 뒤 Pipeline, Orchestrator, 각 Agent, MemoryManager까지 결과가 이어지는지 확인합니다. 주요 확인 항목은 BLIP caption, final prompt, output image, CLIP score, reflection, retry decision, best result, memory 저장, agent trace입니다.

## Q: Known Issues를 문서화한 이유는 무엇인가요?

A: 실제 모델과 API를 사용하는 프로젝트는 token, network, model download, score 한계 같은 변수가 있습니다. Known Issues를 문서화하면 현재 시스템의 한계를 투명하게 설명하고, 다음 개선 방향도 명확히 제시할 수 있습니다.

## Q: CLIP score의 한계는 무엇인가요?

A: CLIP score는 image-text alignment를 평가하는 데 유용하지만 이미지의 미적 품질, 해상도, 세부 왜곡, 사용자 취향까지 평가하지는 못합니다.

## Q: 면접 시연에서는 어떤 흐름으로 보여줄 건가요?

A: 먼저 Gradio UI를 실행하고, 이미지를 업로드한 뒤 user prompt를 입력합니다. 이후 caption, final prompt, generated image, score, reflection, retry decision, best result, agent trace, memory 기록 순서로 설명합니다.

## Q: 이 프로젝트에서 실제로 구현된 모델은 무엇인가요?

A: Vision 단계에는 BLIP image captioning 구조를 구현했고, Generation 단계에는 Hugging Face FLUX API 연동 구조를 구현했으며, Evaluation 단계에는 CLIP image-text similarity 평가 구조를 구현했습니다. 단, FLUX는 Hugging Face token 환경변수가 없거나 API 호출이 실패하면 fallback image를 사용합니다.

## Q: FLUX 연동은 어떻게 했나요?

A: `GenerationAgent`가 직접 API를 호출하지 않고 `FluxTool`을 호출합니다. `FluxTool`은 로컬 Hugging Face token 환경변수가 있으면 Hugging Face `InferenceClient`로 `black-forest-labs/FLUX.1-schnell` 생성을 시도하고, 실패하거나 token이 없으면 PIL 기반 fallback image를 생성합니다.

## Q: 생성 결과와 테스트 기록은 어떻게 관리했나요?

A: runtime output은 `outputs/`에 저장하지만 전체 폴더를 Git에 올리는 방식은 권장하지 않습니다. 선별된 demo 이미지는 `assets/demo/`에 따로 보관하는 방식으로 관리합니다. 실행 기록은 `MemoryManager`가 `memory/history.json`에 caption, prompt, score, retry, best result 등을 저장합니다.

## Q: PlannerAgent는 왜 필요한가요?

A: 기존 workflow는 고정 순서로 실행됐지만, 실제 agentic workflow에서는 입력과 목표에 따라 필요한 작업 순서를 계획하는 단계가 필요합니다. PlannerAgent는 user prompt와 image 제공 여부를 보고 execution plan을 생성합니다.

## Q: 현재 PlannerAgent는 실제 LLM인가요?

A: 아닙니다. 현재는 rule-based PlannerAgent입니다. 조건이 명확하고 디버깅하기 쉬운 방식으로 먼저 Planner와 Orchestrator의 책임 분리를 학습하기 위해 도입했습니다.

## Q: PlannerAgent와 OrchestratorAgent의 차이는 무엇인가요?

A: PlannerAgent는 실행 계획을 생성합니다. OrchestratorAgent는 그 계획을 기록하고 실제 agent workflow를 실행합니다. 즉 Planner는 planning, Orchestrator는 execution coordination에 집중합니다.

## Q: 왜 동적 실행 엔진을 바로 만들지 않았나요?

A: dynamic execution engine은 branch, skipped step, dependency, failure handling까지 포함해 복잡도가 큽니다. 이번 Sprint에서는 먼저 plan 생성과 기록을 안정화하고, 기존 E2E workflow를 유지하는 것을 목표로 했습니다.

## Q: ToolRegistry는 왜 필요한가요?

A: Agent와 Tool이 늘어나면 Orchestrator가 모든 구현 객체를 직접 알고 호출하는 구조가 복잡해집니다. ToolRegistry는 이름 기반으로 callable을 등록하고 호출하게 해 Orchestrator와 개별 Agent/Tool 사이의 결합을 줄입니다.

## Q: PlannerAgent와 ToolRegistry의 차이는 무엇인가요?

A: PlannerAgent는 무엇을 실행할지 계획을 만듭니다. ToolRegistry는 그 이름에 해당하는 callable을 찾아 실행하는 호출 계층입니다. 즉 Planner는 plan, Registry는 call dispatch를 담당합니다.

## Q: OrchestratorAgent가 직접 Agent를 호출하지 않게 만든 이유는 무엇인가요?

A: 직접 호출 구조는 Agent가 늘어날수록 Orchestrator가 구현 세부사항에 강하게 결합됩니다. Registry를 사용하면 Orchestrator는 step name 중심으로 호출하고, 실제 객체 관리는 Registry가 담당합니다.

## Q: 이 구조가 MCP나 Tool Calling과 어떻게 연결되나요?

A: 현재는 Python class 기반 local registry지만, 개념적으로는 tool name으로 기능을 호출하는 구조입니다. 향후 schema, remote tool server, MCP integration으로 확장할 수 있습니다.

## Q: 왜 이번 Sprint에서 완전한 dynamic execution engine은 만들지 않았나요?

A: dynamic engine은 plan step별 argument mapping과 error recovery가 필요합니다. 이번 Sprint에서는 기존 E2E 안정성을 유지하면서 registry 기반 호출 구조만 먼저 도입했습니다.

## Q: Context Engineering이란 무엇인가요?

A: Context Engineering은 agent가 사용할 정보를 무작정 많이 넣는 것이 아니라, 필요한 정보를 선별해 의사결정이나 prompt 생성에 적합한 형태로 구성하는 작업입니다.

## Q: PromptAgent가 Memory를 직접 읽지 않는 이유는 무엇인가요?

A: PromptAgent가 MemoryManager를 직접 호출하면 prompt 생성 책임과 storage 접근 책임이 섞입니다. Orchestrator가 context를 구성하고 PromptAgent는 전달받은 context만 사용하는 것이 역할 분리에 더 적합합니다.

## Q: Orchestrator가 context를 구성하는 이유는 무엇인가요?

A: Orchestrator는 planner result, last run, caption, user prompt 등 workflow state를 모두 알고 있습니다. 따라서 context composition을 Orchestrator가 담당하면 각 agent가 자기 책임에 집중할 수 있습니다.

## Q: 이전 best_prompt를 prompt에 반영할 때 주의할 점은 무엇인가요?

A: 이전 prompt를 그대로 길게 복사하면 prompt가 장황해지고 불필요한 정보가 섞일 수 있습니다. 따라서 짧게 요약하거나 "inspired by previous successful prompt" 정도로 제한적으로 반영해야 합니다.

## Q: 이 구조가 RAG와 어떻게 연결되나요?

A: 현재는 JSON memory의 last run만 context로 사용하지만, 향후 semantic memory나 style library를 검색해 prompt context에 넣으면 RAG-style prompt building으로 확장할 수 있습니다.

## Q: Sprint Book은 왜 만들었나요?

A: 프로젝트가 여러 Sprint를 거치며 agent, tool, memory, UI, planning으로 확장됐기 때문에 단순 로그만으로는 설계 의도를 설명하기 어렵습니다. Sprint Book은 각 Sprint마다 왜 설계했는지, 무엇을 배웠는지, 면접에서 어떻게 설명할지를 같은 형식으로 정리하기 위한 문서 시스템입니다.

## Q: Sprint Book은 면접에서 어떻게 활용하나요?

A: 먼저 Sprint Book README로 전체 architecture evolution을 보여주고, 질문이 나오면 관련 Sprint 문서로 들어가 Design Decision과 Interview Talking Points를 설명합니다. 예를 들어 CLIP 오류 질문이 나오면 Sprint12에서 model-based evaluation과 debugging experience를 설명할 수 있습니다.

## Q: Codex Prompt Archive를 남기는 이유는 무엇인가요?

A: Codex를 어떻게 사용했는지 투명하게 보여주기 위해서입니다. 단순히 AI가 코드를 만들었다가 아니라, 제가 Files Allowed, Files Forbidden, Done Definition을 설계하고 Codex를 engineering partner로 통제했다는 점을 설명할 수 있습니다.
## Sprint 18 Interview Notes

Q. 왜 Prompt를 압축했나요?
A. Planner와 Memory context를 모두 prompt에 넣으면 prompt가 길어지고 CLIP 77 token 제한 같은 문제가 생길 수 있기 때문입니다.

Q. Context Budget은 무엇인가요?
A. 모델에 전달할 수 있는 context 양을 제한하고, 중요한 정보만 선택하는 설계 기준입니다.

Q. CLIP 77 token 문제는 무엇이었나요?
A. CLIP text encoder는 입력 길이에 제한이 있어 긴 prompt를 그대로 넣으면 sequence length 오류가 발생할 수 있습니다.

Q. LLM에서도 같은 문제가 발생하나요?
A. 네. LLM은 context window가 더 크지만 무한하지 않기 때문에 불필요한 context는 비용과 품질 문제를 만듭니다.
## Sprint 19 Interview Notes

Q. Dynamic Execution Engine은 왜 필요한가요?
A. PlannerAgent가 만든 `execution_plan`을 실제 실행 흐름에 반영하기 위해 필요합니다. 기존에는 plan이 기록만 되고 실행은 Orchestrator가 고정 순서로 처리했습니다.

Q. PlannerAgent와 ExecutionEngine의 차이는 무엇인가요?
A. PlannerAgent는 무엇을 실행할지 계획하고, ExecutionEngine은 그 계획을 실제 agent/tool 호출로 실행합니다.

Q. state dict는 어떤 역할을 하나요?
A. 각 step의 입력과 출력을 저장하는 runtime state입니다. 예를 들어 caption, final_prompt, score, retry result가 state에 누적됩니다.

Q. 왜 Orchestrator가 직접 실행하지 않게 만들었나요?
A. Orchestrator의 책임을 coordination으로 제한하고, step execution과 state transition은 ExecutionEngine으로 분리하기 위해서입니다.

Q. 이 구조가 LangGraph와 어떤 점에서 유사하고 다른가요?
A. plan, state, node execution이라는 아이디어는 유사하지만, 현재 구현은 외부 framework 없이 Python class와 dict 기반으로 만든 MVP입니다.
## Sprint 20 Interview Notes

Q. 왜 처음부터 ChromaDB를 쓰지 않았나요?
A. 먼저 RAG의 핵심인 Retrieval과 Augmentation 책임 분리를 검증하기 위해 JSON 기반으로 시작했습니다.

Q. KnowledgeManager는 왜 필요한가요?
A. RetrievalAgent가 JSON 파일 구조를 직접 알지 않도록 storage access layer를 분리하기 위해 필요합니다.

Q. RetrievalAgent는 무엇을 검색하나요?
A. caption과 user prompt를 기반으로 style, lighting, composition, quality, negative prompt rule을 검색합니다.

Q. PromptAgent와 RetrievalAgent의 차이는 무엇인가요?
A. RetrievalAgent는 지식을 찾고, PromptAgent는 압축된 context와 user input을 바탕으로 final prompt를 생성합니다.

Q. 나중에 Vector DB로 어떻게 확장할 계획인가요?
A. KnowledgeManager의 내부 구현을 JSON loader에서 ChromaDB, FAISS, Milvus adapter로 교체하고 RetrievalAgent interface는 유지할 수 있습니다.
## Sprint 21 Interview Notes

Q. Semantic Memory와 Episodic Memory의 차이는 무엇인가요?
A. Episodic Memory는 실행 기록 자체이고, Semantic Memory는 현재 요청과 관련 있는 과거 지식을 검색해 활용하는 구조입니다.

Q. 왜 memory_retrieval을 vision 이후에 실행하나요?
A. caption이 있어야 이미지 내용과 user prompt를 결합한 더 좋은 검색 query를 만들 수 있기 때문입니다.

Q. 왜 Vector DB를 바로 쓰지 않았나요?
A. 먼저 memory retrieval interface와 workflow 위치를 검증하기 위해 JSON keyword similarity로 시작했습니다.

Q. Memory 검색 결과를 prompt에 그대로 넣지 않는 이유는 무엇인가요?
A. full history는 길고 noise가 많기 때문에 prompt budget을 초과할 수 있습니다. 그래서 짧은 memory hint만 사용합니다.

Q. 이 구조를 ChromaDB로 어떻게 확장할 수 있나요?
A. `MemoryManager.get_memory_context()` 내부 구현을 embedding search로 바꾸고 외부 interface는 유지하면 됩니다.
## Sprint 22 Interview Notes

Q. PromptAgent 하나가 아닌 여러 Agent로 나눈 이유는?
A. 실제 image prompt는 character, style, layout, lighting, negative prompt처럼 서로 다른 역할이 있기 때문입니다. 역할별 agent로 나누면 디버깅과 확장이 쉬워집니다.

Q. PromptAssembler는 왜 필요한가요?
A. 여러 agent가 만든 fragment를 일관된 generation prompt로 조립하는 전담 책임이 필요하기 때문입니다.

Q. Prompt Routing이란?
A. prompt 생성 요청을 역할에 따라 적절한 agent로 보내는 구조입니다.

Q. 이 구조가 AI Agent와 어떤 관련이 있나요?
A. 각 agent가 독립적인 역할과 출력을 가지고 협업해 하나의 prompt를 완성하므로 multi-agent collaboration 구조입니다.
## Sprint22 Detailed Interview Notes

Q. Prompt Orchestration이란 무엇인가요?
A. 하나의 PromptAgent가 모든 것을 처리하지 않고, character/style/layout/pose/expression/negative prompt agent가 각 section을 만들고 PromptAssembler가 최종 generation prompt를 조립하는 구조입니다.

Q. negative_prompt를 따로 분리한 이유는 무엇인가요?
A. negative prompt는 provider별로 별도 필드가 될 수 있고, positive generation prompt에 섞으면 의미가 흐려질 수 있기 때문입니다.

Q. 이 구조가 ChatGPT 이미지 생성 방식과 어떤 점에서 유사한가요?
A. 사용자는 자연어로 요청하지만 내부적으로는 character, style, layout, pose 같은 구조화된 prompt section으로 분해한다는 점이 유사합니다.
## Sprint23 Interview Notes

Q. Character Reference Handling이란 무엇인가요?
A. uploaded reference image를 character identity source로 보고 generation prompt에 identity preservation rule을 반영하는 구조입니다.

Q. 여러 reference image가 있을 때 캐릭터가 섞이는 문제를 어떻게 방지하나요?
A. 각 image를 one separate character로 취급하고 `do not merge characters` rule을 prompt에 포함합니다.

Q. 왜 UI보다 내부 schema를 먼저 만들었나요?
A. UI 변경 전에도 character reference semantics를 안정화하고 single-image workflow를 깨지 않기 위해서입니다.

Q. CharacterAgent와 PromptAssembler의 역할 차이는 무엇인가요?
A. CharacterAgent는 character schema를 만들고, PromptAssembler는 그 schema를 generation prompt rule로 조립합니다.
## Sprint24 Interview Notes

Q. LayoutAgent는 Prompt를 만드는 Agent인가요?
A. LayoutAgent는 final prompt를 직접 만들기보다 layout plan을 만들고, PromptAssembler가 이를 generation prompt로 변환합니다.

Q. Composition Planning이 중요한 이유는?
A. 생성 결과의 frame, camera, subject placement, cropping이 prompt 품질에 큰 영향을 주기 때문입니다.

Q. Camera View를 Prompt에서 분리한 이유는?
A. camera view는 style이나 character와 다른 visual structure decision이므로 LayoutAgent에서 별도로 관리하는 것이 명확합니다.
## Sprint25 Interview Notes

Q. ScenePlanningAgent는 왜 필요한가요?
A. 사용자 요청의 전체 상황을 먼저 구조화해야 Layout, Pose, Expression이 같은 의도를 공유할 수 있기 때문입니다.

Q. Scene Plan과 Layout Plan의 차이는 무엇인가요?
A. Scene Plan은 장면의 의미와 관계를 설명하고, Layout Plan은 화면 구성과 카메라 배치를 설명합니다.

Q. 왜 rule-based로 시작했나요?
A. schema와 workflow 위치를 검증하기 위해 예측 가능한 rule-based planner로 시작했습니다.

Q. Scene Plan은 PoseAgent와 ExpressionAgent에 어떻게 영향을 주나요?
A. relationship, interaction, emotion 값이 pose_rules와 expression_rules에 반영됩니다.
## Sprint26 Interview Notes

Q. ProviderPromptAdapter는 왜 필요한가요?
A. provider마다 prompt 해석 방식이 다르기 때문에 canonical prompt를 provider별 prompt로 변환해야 합니다.

Q. Canonical Prompt는 무엇인가요?
A. 특정 provider에 종속되지 않은 이미지 생성 의도입니다.

Q. 왜 GenerationAgent를 직접 수정하지 않았나요?
A. GenerationAgent는 생성 실행 책임을 유지하고, prompt 최적화는 adapter layer가 담당하도록 분리하기 위해서입니다.
## Sprint27 Interview Notes

Q. ProviderRouter는 왜 필요한가요?
A. provider 선택과 prompt 변환을 분리해 provider 확장성을 높이기 위해 필요합니다.

Q. ProviderRouter와 ProviderPromptAdapter의 차이는 무엇인가요?
A. ProviderRouter는 어떤 provider를 쓸지 고르고, ProviderPromptAdapter는 선택된 provider에 맞게 prompt를 변환합니다.

Q. 현재 FLUX만 사용하는데 왜 필요한가요?
A. 지금은 fallback 구조지만, 나중에 SDXL/GPT Image/Imagen을 연결할 때 선택 계층을 그대로 사용할 수 있습니다.

Q. unsupported provider 요청은 어떻게 처리하나요?
A. 현재 available provider가 아니면 fallback provider인 FLUX를 선택합니다.
## Sprint28 Interview Notes

Q. 왜 Config-driven architecture를 적용했나요?
A. provider capability를 코드에 직접 박아두면 provider가 늘어날 때마다 Router 코드를 수정해야 합니다. `providers.json`으로 분리하면 provider 활성화 여부, capability, display name을 설정 파일에서 관리할 수 있어 확장성이 좋아집니다.

Q. Provider Registry와 ProviderRouter의 차이는 무엇인가요?
A. Provider Registry는 provider의 capability와 enabled 상태를 보관하는 설정 계층이고, ProviderRouter는 그 설정을 읽어 현재 요청에 맞는 provider를 선택하는 실행 계층입니다.

Q. 왜 현재는 FLUX만 enabled인가요?
A. 현재 실제 workflow는 FLUX 중심으로 검증되어 있습니다. GPT Image와 SDXL은 capability 정보만 등록하고 `enabled: false`로 두어, 향후 연결 시 config 변경만으로 routing 후보에 넣을 수 있게 했습니다.

## Sprint29 Interview Notes

Q. PromptCriticAgent는 무엇인가요?
A. PromptAssembler가 만든 canonical prompt를 generation 전에 점검하는 Agent입니다. 중복 keyword, 누락 section, prompt 길이, 품질 점수를 rule-based로 분석합니다.

Q. 왜 Generation 전에 Prompt를 검토하나요?
A. 이미지 생성은 비용과 시간이 드는 단계입니다. generation 전에 prompt 문제를 발견하면 provider 호출 전에 품질 저하 원인을 확인할 수 있습니다.

Q. Prompt 품질은 어떻게 평가하나요?
A. 현재는 100점에서 시작해 duplicate keyword, missing section, 너무 긴 prompt, 너무 짧은 prompt에 감점을 적용합니다. 향후에는 LLM critic이나 provider-specific critic으로 확장할 수 있습니다.

## Sprint30A Interview Notes

Q. 왜 Agent 인터페이스를 `run(state)`로 통일했나요?
A. Agent가 늘어날수록 ExecutionEngine이 step별 인자를 직접 관리하면 복잡해집니다. state 기반으로 통일하면 각 Agent가 필요한 값을 직접 읽고, 자신이 만든 결과만 dict로 반환할 수 있습니다.

Q. ExecutionEngine은 왜 단순해지나요?
A. 장기적으로는 `result = registry.run_with_state(step, state)`와 `state.update(result)` 패턴으로 대부분의 step을 처리할 수 있기 때문입니다.

Q. 왜 모든 Agent를 한 번에 바꾸지 않았나요?
A. BLIP/FLUX/CLIP, retry, memory, UI까지 동시에 바꾸면 E2E 안정성이 떨어집니다. 이번 Sprint는 prompt/provider 계층부터 점진적으로 적용했습니다.

Q. LangGraph와 어떤 점에서 유사한가요?
A. 각 Agent를 state를 입력받고 partial state를 반환하는 node처럼 다룬다는 점이 유사합니다. 다만 현재는 외부 framework 없이 Python class 기반으로 구현합니다.

Q. state dict 방식의 장단점은 무엇인가요?
A. 장점은 확장성과 실행 엔진 단순화입니다. 단점은 key 이름 관리가 느슨해질 수 있다는 점이며, 향후 AgentState dataclass로 보완할 수 있습니다.

## Sprint31 Interview Notes

Q. PromptOptimizerAgent는 왜 필요한가요?
A. PromptCriticAgent가 문제를 발견해도 그 결과가 prompt에 반영되지 않으면 generation 품질 개선으로 이어지지 않습니다. Optimizer는 critique 결과를 실제 prompt 수정으로 연결합니다.

Q. PromptCritic과 PromptOptimizer의 차이는 무엇인가요?
A. PromptCritic은 분석과 진단을 담당하고, PromptOptimizer는 중복 제거, 누락 보완, 길이 조절 같은 수정을 담당합니다.

Q. 왜 Generation 전에 prompt를 최적화하나요?
A. generation 이후에 문제를 찾는 것보다 generation 전에 prompt를 정리하는 것이 비용과 시간을 줄이고 결과 품질을 안정화합니다.

Q. rule-based optimizer의 한계는 무엇인가요?
A. 의미적 모호성이나 고급 미학 판단은 어렵습니다. 하지만 deterministic하고 디버깅하기 쉬워 초기 architecture 검증에 적합합니다.

Q. LLM 기반 optimizer로 어떻게 확장할 수 있나요?
A. 현재 optimization_report와 prompt_report를 LLM 입력으로 사용해 semantic rewrite, provider-specific rewrite, A/B prompt 후보 생성을 추가할 수 있습니다.

## Sprint32 Interview Notes

Q. PromptOptimizer는 무엇을 기준으로 Prompt를 수정하는가?
A. PromptCriticAgent가 만든 `prompt_report`를 기준으로 수정합니다. duplicate keyword, missing section, warning, quality score를 먼저 읽고 필요한 작업만 수행합니다.

Q. Rule 기반 Optimizer와 Intelligent Optimizer의 차이는?
A. 기존 rule 기반 Optimizer는 정해진 정리 작업을 넓게 적용했습니다. Intelligent Optimizer는 Critic Report를 해석해 중복이 있을 때만 제거하고, 누락된 section만 보완하며, warning이 있을 때만 길이 조절을 수행합니다.

Q. Critic Report를 어떻게 활용하는가?
A. `duplicate_keywords`는 중복 제거에, `missing_sections`는 필요한 keyword 추가에, `warnings`는 압축 또는 보강 판단에, `quality_score`는 수정 강도 조절에 사용합니다.

## Sprint33 Interview Notes

Q. LLMPromptOptimizerAgent는 왜 필요한가요?
A. rule-based optimizer는 안정적이지만 긴 prompt를 자연스럽게 재작성하거나 복잡한 의도를 조정하는 데 한계가 있습니다. LLMPromptOptimizerAgent는 향후 GPT, Claude, Gemini, local LLM 등을 붙일 수 있는 확장 지점입니다.

Q. 실제 LLM API를 바로 붙이지 않은 이유는 무엇인가요?
A. 이번 Sprint의 목표는 interface-first 설계입니다. API key, 비용, 네트워크, provider 장애를 도입하기 전에 disabled/mock/fallback 구조를 먼저 검증했습니다.

Q. Rule-based Optimizer와 LLM Optimizer의 차이는 무엇인가요?
A. Rule-based Optimizer는 deterministic한 규칙으로 중복 제거와 누락 보완을 수행합니다. LLM Optimizer는 향후 자연스러운 rewrite와 semantic intent 조정을 담당할 수 있습니다.

Q. fallback strategy가 왜 중요한가요?
A. optional LLM service가 실패해도 BLIP/FLUX/CLIP workflow, retry, memory가 계속 동작해야 하기 때문입니다.

Q. 나중에 OpenAI API를 붙이려면 어디를 수정하나요?
A. `LLMPromptOptimizerAgent._run_llm_optimizer()` 내부에 provider client 호출을 추가하면 됩니다. 현재는 외부 API 호출 없이 fallback report를 반환합니다.

## Sprint34 Interview Notes

Q. 왜 dict 대신 AgentState를 도입했나요?
A. Agent가 많아지면서 `caption`, `scene_plan`, `provider_prompt`, `prompt_report` 같은 key가 계속 늘어납니다. AgentState는 공통 state key를 한 곳에서 관리하고 validation warning을 제공하기 위해 도입했습니다.

Q. Typed State의 장점은 무엇인가요?
A. 상태 필드를 명시적으로 볼 수 있고, 오타나 누락 가능성을 줄일 수 있습니다. 향후 IDE 지원과 schema validation으로 확장하기도 쉽습니다.

Q. 왜 dataclass를 사용했나요?
A. dataclass는 가볍고 Python 표준 기능이며, framework core 상태 객체를 빠르게 정의하기에 적합합니다.

Q. Framework 관점에서 어떤 장점이 있나요?
A. AgentState는 ExecutionEngine, ToolRegistry, Agent 사이의 공통 계약 역할을 합니다. 나중에 graph state, multi-session state, distributed agent state로 확장할 기반이 됩니다.

## Sprint35 Interview Notes

Q. 왜 FastAPI를 추가했나요?
A. Gradio는 사람이 직접 사용하는 데모 UI에 적합하고, FastAPI는 외부 프로그램이 REST API로 agent workflow를 호출하기에 적합합니다.

Q. Gradio와 FastAPI의 차이는?
A. Gradio는 빠른 UI 실험용이고, FastAPI는 backend service layer입니다. FastAPI는 Swagger/OpenAPI 문서를 자동 제공하고 다른 서비스와 연동하기 쉽습니다.

Q. 왜 Service Layer를 분리했나요?
A. API route가 ExecutionEngine을 직접 알면 API와 framework가 강하게 결합됩니다. `service.py`를 두면 route는 요청/응답에 집중하고 service layer가 orchestration 호출을 담당합니다.

## Sprint36 Interview Notes

Q. Debug Report는 왜 필요한가요?
A. 최종 이미지가 마음에 들지 않을 때 어떤 Agent 단계에서 문제가 생겼는지 추적하기 위해 필요합니다.

Q. prompt_preview.txt와 report.json을 나눈 이유는 무엇인가요?
A. `report.json`은 구조화된 데이터라 자동 분석에 좋고, `prompt_preview.txt`는 사람이 빠르게 읽고 설명하기 좋습니다.

Q. Agent pipeline은 어떻게 디버깅하나요?
A. run 폴더의 report와 preview를 보고 scene plan, layout, critic report, optimizer report, provider prompt, evaluation score, retry 결과를 순서대로 확인합니다.

Q. 생성 결과가 마음에 들지 않을 때 어디를 확인하나요?
A. 먼저 prompt_preview에서 canonical/provider/evaluation prompt를 보고, report.json에서 prompt critic과 optimizer report, CLIP score, retry 결과를 확인합니다.

Q. 이 구조가 실제 서비스 운영과 어떻게 연결되나요?
A. 서비스에서는 장애나 품질 저하를 run 단위로 추적해야 합니다. Debug report는 향후 UI Trace Viewer, benchmark dashboard, observability API로 확장할 수 있습니다.

## Sprint37 Interview Notes

Q. Benchmark Runner는 왜 필요한가요?
A. 한두 개 prompt의 결과만 보면 agent framework의 품질을 판단하기 어렵습니다. 여러 prompt를 반복 실행하고 score, retry, provider, debug report path를 저장하면 개선 효과를 비교할 수 있습니다.

Q. 실패한 prompt는 어떻게 처리하나요?
A. 한 prompt가 실패해도 전체 benchmark는 계속 진행합니다. 실패 항목은 `success=false`와 error message로 결과 JSON에 저장합니다.

Q. Debug Report와 Benchmark는 어떻게 연결되나요?
A. Benchmark 결과에는 각 run의 `debug_report_path`와 `prompt_preview_path`가 포함됩니다. 점수가 낮은 항목은 해당 report를 열어 prompt lifecycle을 추적할 수 있습니다.

## Sprint38 Interview Notes

Q. Benchmark Report는 왜 만들었나요?
A. benchmark 결과 JSON은 기계가 읽기 좋지만 사람이 비교하기 어렵습니다. Markdown/HTML report는 score, retry, provider, debug path를 한눈에 비교할 수 있게 합니다.

Q. CLIP score만으로 품질을 판단할 수 있나요?
A. 어렵습니다. CLIP score는 prompt-image semantic similarity에 가깝고, 구도나 미감 같은 absolute image quality와는 다릅니다.

Q. Debug Report와 Benchmark Report의 차이는 무엇인가요?
A. Debug Report는 한 run의 세부 lifecycle을 보여주고, Benchmark Report는 여러 run을 비교합니다.

Q. 실험 결과를 어떻게 비교했나요?
A. benchmark result JSON을 읽어 total, average best_score, retry rate, best/worst run, failed runs, result table로 정리했습니다.
