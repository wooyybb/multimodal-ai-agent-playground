# Interview Notes

## v1.0 RC1 Layer-based Questions

Q. 이 프로젝트는 단순 이미지 생성 데모와 무엇이 다른가요?
A. 단순 데모는 보통 prompt를 넣고 이미지를 받는 흐름에서 끝납니다. 이 프로젝트는 Planning, Context, Generation, Evaluation, Reasoning, Memory / Observability Layer로 나누어 입력 이해부터 평가, 재계획, 기록까지 관리합니다. 그래서 결과만 보는 것이 아니라 시스템이 무엇을 이해했고 왜 그런 결정을 했는지 추적할 수 있습니다.

Q. 왜 Layer 구조로 정리했나요?
A. Agent 수가 많아지면 개별 클래스 이름만으로는 전체 구조를 이해하기 어렵습니다. Layer 구조는 각 Agent가 어떤 책임 영역에 속하는지 보여주기 위한 설명 방식입니다. 기능을 새로 만든 것이 아니라, 기존 기능을 유지하면서 유지보수와 포트폴리오 설명이 쉬운 구조로 정리했습니다.

Q. Agent가 많아졌을 때 복잡도를 어떻게 관리했나요?
A. DynamicExecutionEngine은 실행 순서를 관리하고, ToolRegistry는 step 이름과 실제 Agent 객체를 분리합니다. 문서에서는 각 Agent를 6개 Layer에 배치해 책임을 정리했습니다. 이 방식은 새로운 Agent가 추가되어도 어느 Layer에 속하는지 먼저 결정하게 만들어 구조적 복잡도를 줄입니다.

Q. Planning Layer와 Reasoning Layer의 차이는 무엇인가요?
A. Planning Layer는 생성 전에 user intent, reference image, goal, scene, character identity를 해석합니다. Reasoning Layer는 생성 후 evaluation 결과를 바탕으로 실패 원인, 전략 선택, self verification, adaptive planning을 수행합니다. 즉 Planning은 사전 계획이고 Reasoning은 결과 기반 판단과 재계획입니다.

Q. Context Program은 왜 필요한가요?
A. Prompt 문자열을 바로 만들면 provider 제약, memory, retrieval, character identity, layout 정보가 섞여 관리하기 어렵습니다. Context Program은 이런 정보를 provider-independent structured object로 정리합니다. 이후 PromptCompiler가 이 구조를 FLUX, SDXL, GPT Image 같은 provider별 prompt package로 변환할 수 있습니다.

Q. Adaptive Planning은 단순 Retry와 무엇이 다른가요?
A. Retry는 다시 생성할지 여부를 판단하는 정책에 가깝습니다. Adaptive Planning은 왜 실패했는지 분석하고, character priority, layout rule, style balance 같은 context update를 만들어 다음 생성 전략을 바꿉니다. 그래서 단순 반복이 아니라 re-planning loop에 가깝습니다.

Q. Evaluation Layer를 왜 Multi-Metric 구조로 만들었나요?
A. CLIP similarity 하나만으로는 identity preservation, prompt completeness, aesthetic quality를 충분히 설명하기 어렵습니다. Multi-Metric Evaluation은 CLIP, Identity, Prompt, Aesthetic metric을 분리하고 weighted score와 reason을 남깁니다. 이 구조는 나중에 PickScore, DINO, VLM Judge 같은 metric을 추가하기 쉽습니다.

Q. 이 프로젝트를 실제 서비스로 확장한다면 무엇을 개선하겠습니까?
A. 먼저 Docker/CI smoke test, queue-based async generation, persistent database, object storage, auth, monitoring을 추가해야 합니다. 그 다음 multi-session memory와 benchmark dashboard를 붙여 운영 중 품질 변화를 추적할 수 있게 만들겠습니다. 또한 VLM Judge나 stronger VLM을 추가해 reference image parsing과 evaluation 품질을 높일 수 있습니다.

## Key Portfolio Questions

Q. 이 프로젝트는 단순 이미지 생성 데모와 무엇이 다른가요?
A. 단순 prompt-to-image가 아니라 Vision Understanding, Context Engineering, Prompt Compiler, Provider Routing, Multi-Metric Evaluation, Reflection, Self Verification, Strategy Selection, Adaptive Planning, Memory까지 포함한 전체 AI Agent workflow입니다.

Q. Context Program은 무엇인가요?
A. Context Program은 user intent, caption, character program, goal tree, memory, retrieval, layout, style, provider constraint를 provider-independent structured object로 정리한 중간 표현입니다. Prompt 이전 단계의 의미 구조입니다.

Q. Prompt Compiler는 왜 필요한가요?
A. Context Program은 provider-independent 구조이고, FLUX/SDXL/GPT Image 같은 provider는 서로 다른 prompt 형식이 필요합니다. Prompt Compiler는 structured context를 provider-specific prompt package로 변환합니다.

Q. Adaptive Planning은 Retry와 무엇이 다른가요?
A. Retry는 다시 생성할지 결정하는 정책이고, Adaptive Planning은 왜 실패했는지 분석한 뒤 context update와 priority change를 만들어 다음 generation 전략을 바꾸는 re-planning 단계입니다.

Q. Multi-Metric Evaluation을 도입한 이유는 무엇인가요?
A. CLIP만으로는 identity preservation, prompt completeness, aesthetic quality를 설명하기 어렵습니다. Multi-Metric Evaluation은 CLIP, Identity, Prompt, Aesthetic metric을 분리하고 weighted score와 reason을 남깁니다.

Q. 실제 서비스로 확장하려면 무엇을 추가해야 하나요?
A. Docker/CI, queue-based async execution, auth, persistent database, object storage, monitoring, benchmark dashboard, multi-session memory, stronger provider error handling이 필요합니다.

## Table of Contents

- [Architecture](#architecture)
- [Agents](#agents)
- [Prompt and Context](#prompt-and-context)
- [Provider and Models](#provider-and-models)
- [Evaluation and Retry](#evaluation-and-retry)
- [Memory and Retrieval](#memory-and-retrieval)
- [Debugging and Benchmark](#debugging-and-benchmark)
- [AI Collaboration](#ai-collaboration)
- [Future Work](#future-work)

## Architecture

Q. 이 프로젝트는 무엇인가요?
A. Planning, Retrieval, Prompt Orchestration, Provider Routing, Generation, Evaluation, Reflection, Retry, Memory를 연결한 multi-agent image generation framework입니다.

Q. 왜 multi-agent 구조인가요?
A. 이미지 생성 workflow는 captioning, context retrieval, prompt assembly, provider adaptation, evaluation처럼 역할이 다릅니다. 각 역할을 Agent로 분리하면 디버깅과 설명이 쉬워집니다.

Q. OrchestratorAgent는 왜 필요한가요?
A. 여러 Agent를 직접 연결하는 진입점입니다. 실제 실행은 DynamicExecutionEngine과 ToolRegistry가 담당하지만, Orchestrator는 agent registration과 pipeline facade 역할을 합니다.

Q. DynamicExecutionEngine의 역할은 무엇인가요?
A. Planner가 만든 execution plan을 읽고 각 step을 순서대로 실행합니다.

Q. ToolRegistry는 왜 필요한가요?
A. Agent 이름과 실행 객체를 분리해 workflow가 직접 class를 의존하지 않도록 합니다.

Q. AgentState를 도입한 이유는?
A. dict key가 많아지면서 오타와 누락 위험이 커졌기 때문입니다. AgentState는 shared state의 중심 계약입니다.

## Agents

Q. VisionAgent는 무엇을 하나요?
A. 입력 이미지를 caption으로 변환합니다. BLIP integration 또는 fallback captioning을 사용합니다.

Q. ScenePlanningAgent는 왜 필요한가요?
A. user prompt를 scene, emotion, relationship, camera intent 등 시각적 계획으로 바꿉니다.

Q. LayoutAgent는 keyword generator인가요?
A. 현재는 composition planning agent입니다. layout type, frame structure, camera view, subject placement를 계획합니다.

Q. Prompt specialist agents를 여러 개로 나눈 이유는?
A. character, style, layout, pose, expression, lighting, negative prompt는 서로 다른 prompt responsibility를 가지기 때문입니다.

Q. PromptAssembler는 왜 필요한가요?
A. specialist output을 canonical prompt로 조립하는 책임을 분리하기 위해서입니다.

## Prompt and Context

Q. Context Engineering이란?
A. Agent가 사용할 task, memory, retrieval, scene, provider constraint를 구조화하는 작업입니다.

Q. Rule 기반과 LLM 기반 Reasoning 차이는?
A. Rule 기반은 빠르고 결정적이며 fallback에 적합합니다. LLM 기반 Reasoning은 semantic conflict, priority, strategy처럼 문맥 해석이 필요한 판단에 강하지만 API 실패와 JSON parsing 실패 가능성이 있으므로 항상 rule fallback을 유지합니다.

Q. 왜 Reasoner Provider Router를 만들었나요?
A. Agent가 OpenAI 같은 특정 provider를 직접 호출하면 교체와 테스트가 어려워집니다. ReasonerRouter는 `LLM_PROVIDER`에 따라 rule, openai, gemini skeleton, claude skeleton을 선택하고 같은 JSON interface로 결과를 반환합니다.

Q. LLM 실패 시 어떻게 동작하나요?
A. API key가 없거나 client import가 실패하거나 JSON parsing이 실패하면 기존 rule 결과를 그대로 fallback으로 사용합니다. Debug metadata에는 provider, fallback 여부, latency, fallback reason을 남깁니다.

Q. 왜 LLM을 Prompt 생성에 쓰지 않고 Reasoning에 먼저 사용했나요?
A. Prompt를 바로 생성하게 하면 내부 의도 해석과 provider prompt가 섞이기 쉽습니다. 먼저 semantic planning을 구조화하면 rule-based agent와 prompt compiler가 더 안정적으로 사용할 수 있습니다.

Q. Semantic Planning Layer란 무엇인가요?
A. user intent를 scene goal, composition goal, interaction goal, style goal, priority 같은 구조화된 계획으로 바꾸는 prompt 이전 단계입니다.

Q. Rule-based Agent와 LLM Agent를 왜 분리했나요?
A. LLM은 의도 해석에 강하고, rule-based agent는 안정적인 구조화와 fallback에 강합니다. 둘을 분리하면 디버깅과 교체가 쉬워집니다.

Q. Context Program이란?
A. 여러 agent output을 provider-independent structured intermediate representation으로 정리한 객체입니다.

Q. ContextProgramBuilder는 왜 만들었나요?
A. agent state와 generation prompt가 섞이지 않게 하기 위해서입니다. 먼저 context를 구조화하고, 이후 prompt로 컴파일합니다.

Q. Context Program Validator는 왜 필요한가요?
A. Context Program이 prompt assembly 전에 필요한 section을 모두 갖췄는지, 타입이 맞는지, provider와 충돌하지 않는지 확인하기 위해서입니다.

Q. Schema validation이 AI Agent Framework에서 중요한 이유는?
A. Agent가 많아질수록 state shape이 불안정해질 수 있습니다. schema validation은 generation 전에 오류를 빨리 발견하고 debug report에 남기는 안전장치입니다.

Q. Provider compatibility는 어떻게 검사하나요?
A. provider별 제약을 rule로 확인합니다. 예를 들어 FLUX는 long prompt와 negative prompt 직접 반영에 warning을 내고, SDXL은 negative section 존재를 확인합니다.

Q. Prompt Engineering과 Context Engineering 차이는?
A. Context Engineering은 정보를 구조화하는 일이고, Prompt Engineering은 그 정보를 모델 입력 문장으로 변환하는 일입니다.

Q. Canonical Prompt는 무엇인가요?
A. provider에 종속되지 않은 기본 generation prompt입니다.

Q. Provider Prompt는 무엇인가요?
A. 특정 provider가 이해하기 좋은 형태로 변환된 prompt입니다.

Q. LLMPromptCriticAgent는 왜 필요한가요?
A. rule-based critic은 중복, 누락, 길이 문제에 강하지만 semantic conflict나 provider suitability를 충분히 보지 못합니다. LLMPromptCriticAgent는 이런 의미 기반 문제를 structured report로 진단합니다.

Q. Rule-based Critic과 LLM Critic의 차이는 무엇인가요?
A. Rule-based Critic은 deterministic check이고, LLM Critic은 의도 충돌, 우선순위, scene/layout/style 적합성을 보는 reasoning layer입니다.

Q. 왜 prompt를 바로 수정하지 않고 critique report만 생성하나요?
A. Critic과 Optimizer 책임을 분리하기 위해서입니다. Critic은 문제를 진단하고, Optimizer가 수정 여부와 방법을 결정합니다.

Q. semantic conflict는 어떻게 감지하나요?
A. 현재 mock mode에서는 user prompt와 canonical prompt의 keyword 충돌을 rule로 감지합니다. 예를 들어 photobooth intent와 battle/combat tone이 같이 있으면 conflict로 기록합니다.

Q. 실제 LLM API를 붙이지 않고 mock으로 시작한 이유는?
A. API key, 비용, 네트워크, provider 실패 없이 interface와 state flow를 먼저 검증하기 위해서입니다.

Q. 왜 LLM Client를 따로 만들었나요?
A. LLMContextReasoner, LLMPromptCritic, LLMPromptOptimizer가 각자 provider 호출 방식을 갖고 있으면 중복과 결합도가 커집니다. LLMClient는 reason, critic, optimize 호출을 공통 interface로 묶습니다.

Q. Provider Registry가 필요한 이유는?
A. mock, openai, gemini, claude, ollama 같은 provider를 agent 코드와 분리해 선택하기 위해서입니다. 지금은 mock만 구현되어 있습니다.

Q. OpenAI 대신 Mock으로 먼저 구현한 이유는?
A. API key, 네트워크, 비용 없이 dependency inversion과 provider strategy 구조를 먼저 검증하기 위해서입니다.

Q. 왜 Provider를 Agent에서 직접 호출하지 않았나요?
A. Agent가 provider API를 직접 알면 교체와 테스트가 어려워집니다. Agent는 LLMClient만 보고, provider 호출 책임은 AIModelService 아래로 숨겼습니다.

Q. AIModelService를 만든 이유는?
A. reason, critic, optimize 요청을 공통 model service boundary에서 처리하고 provider registry로 위임하기 위해서입니다.

Q. Provider Registry와 AIModelService의 차이는?
A. AIModelService는 reason/critic/optimize 요청을 받는 service layer이고, Provider Registry는 provider 이름을 실제 provider 객체로 매핑하는 factory 역할입니다.

Q. 왜 Provider를 Agent에서 직접 호출하지 않았나요?
A. Agent가 OpenAI 같은 특정 provider를 직접 호출하면 교체와 테스트가 어려워집니다. Agent는 LLMClient만 호출하고, 실제 provider 호출은 AIModelService와 ProviderRegistry 뒤에 둡니다.

Q. OpenAI API key가 없으면 어떻게 되나요?
A. OpenAIProvider는 crash하지 않고 warning을 출력한 뒤 MockProvider fallback 결과를 반환합니다. API key는 로그나 문서에 노출하지 않습니다.

Q. OpenAI 응답이 JSON이 아니면 어떻게 처리하나요?
A. raw_text를 저장하고 fallback structure를 반환하며 `used_fallback=true`로 표시합니다.

Q. Evaluation Prompt는 왜 따로 있나요?
A. CLIP token budget을 넘지 않도록 generation prompt보다 짧고 평가 중심으로 설계합니다.

Q. Retry Prompt는 무엇인가요?
A. Reflection 결과를 바탕으로 재시도에 사용하는 압축된 prompt입니다.

## Provider and Models

Q. ProviderRouter는 무엇을 하나요?
A. provider capability config를 읽고 사용 가능한 provider를 선택합니다.

Q. ProviderPromptAdapter는 왜 필요한가요?
A. FLUX, GPT Image, SDXL은 prompt 제약이 다르므로 provider별 변환 레이어가 필요합니다.

Q. PromptCompiler는 왜 필요한가요?
A. Context Program은 provider-independent 구조입니다. PromptCompiler는 이 구조를 FLUX, SDXL, GPT Image가 사용할 수 있는 provider-specific prompt package로 변환합니다.

Q. PromptAssembler와 PromptCompiler의 차이는 무엇인가요?
A. PromptAssembler는 canonical prompt를 만들고, PromptCompiler는 Context Program을 provider-specific package로 컴파일합니다.

Q. Context Program과 compiled prompt package의 차이는 무엇인가요?
A. Context Program은 구조화된 의미 표현이고, compiled prompt package는 provider 입력에 가까운 positive prompt, negative prompt, prompt blocks, budget 정보를 포함합니다.

Q. ProviderPromptAdapter와 PromptCompiler를 분리한 이유는 무엇인가요?
A. Compiler는 provider별 prompt package를 만들고, Adapter는 그 package를 최종 provider input으로 정리합니다. 이 분리로 provider별 컴파일 규칙과 실행 입력 포맷을 따로 관리할 수 있습니다.

Q. 실제 모델은 무엇을 사용하나요?
A. BLIP captioning, FLUX generation, CLIP evaluation path를 사용하며 환경에 따라 fallback이 동작할 수 있습니다.

Q. 왜 fallback을 유지하나요?
A. API token, 모델 로딩, 네트워크 문제로 전체 workflow가 깨지지 않게 하기 위해서입니다.

Q. 왜 LangGraph/CrewAI 없이 만들었나요?
A. 먼저 Python class 기반으로 agent responsibility와 state flow를 직접 학습하기 위해서입니다.

## Evaluation and Retry

Q. CLIP score는 무엇을 의미하나요?
A. image-text semantic similarity에 가깝습니다. 절대적인 이미지 품질 점수는 아닙니다.

Q. ReflectionAgent는 왜 필요한가요?
A. evaluation result를 바탕으로 실패 원인과 개선 방향을 설명합니다.

Q. RetryAgent는 왜 분리했나요?
A. retry 판단 기준을 Reflection과 분리하면 threshold나 policy를 바꾸기 쉽습니다.

Q. Retry loop는 무한 반복인가요?
A. 현재는 안정성을 위해 one-step retry 구조입니다.

## Memory and Retrieval

Q. MemoryManager는 왜 Agent가 아니라 Manager인가요?
A. Memory는 판단 주체라기보다 저장, 조회, 삭제 interface를 제공하는 infrastructure component입니다.

Q. Working Memory와 Episodic Memory 차이는?
A. Working Memory는 현재 run의 context이고, Episodic Memory는 이전 run 기록입니다.

Q. RetrievalAgent는 왜 필요한가요?
A. user prompt와 caption에 맞는 style/context knowledge를 prompt 단계에 공급합니다.

Q. JSON으로 시작한 이유는?
A. 구조가 단순하고 디버깅이 쉬우며, 추후 vector DB로 옮기기 전 interface 검증에 적합하기 때문입니다.

## Debugging and Benchmark

Q. Debug Report는 왜 필요한가요?
A. 한 run에서 어떤 prompt, score, retry, agent trace가 생겼는지 추적하기 위해서입니다.

Q. Prompt Preview는 무엇인가요?
A. 사람이 빠르게 읽을 수 있는 prompt lifecycle summary입니다.

Q. Benchmark Runner는 왜 필요한가요?
A. 여러 prompt를 반복 실행해 score, retry, provider, debug path를 비교하기 위해서입니다.

Q. Benchmark Report는 무엇인가요?
A. benchmark JSON을 Markdown/HTML 요약으로 변환한 비교 리포트입니다.

## AI Collaboration

Q. Codex를 어떻게 활용했나요?
A. Workspace rule과 allowed files를 명확히 주고, sprint별로 구현/문서/검증을 분리해 pair-programming 방식으로 사용했습니다.

Q. Prompt Engineering은 어떻게 했나요?
A. Task, Architecture, Workspace, Allowed Files, Forbidden Files, Requirements, Documentation, Done Definition 순서로 작성했습니다.

Q. 본인이 한 역할은 무엇인가요?
A. architecture 방향, sprint goal, file boundary, 검증 기준을 정하고 결과를 리뷰했습니다. Codex는 구현과 문서 초안 생성을 도왔습니다.

## Vision Provider

Q. 왜 BLIP만 직접 연결하지 않고 VLM Adapter를 만들었나요?
A. BLIP는 captioning에는 충분하지만 object, character, style, relationship parsing에는 한계가 있습니다. VisionAgent가 BLIP에 직접 의존하면 Florence-2나 Qwen-VL로 교체할 때 agent 코드를 계속 바꿔야 하므로, VLMRouter와 provider interface로 분리했습니다.

Q. BLIP의 한계는 무엇인가요?
A. 짧은 caption 생성에는 강하지만 자세한 scene graph, character attributes, layout hints, reference-image understanding을 안정적으로 구조화하기는 어렵습니다.

Q. Florence/Qwen 같은 VLM으로 어떻게 확장할 수 있나요?
A. `BaseVLM.analyze()` 인터페이스만 구현하면 됩니다. provider가 달라져도 VisionAgent는 `caption`과 `vision_result`를 같은 구조로 받습니다.

Q. 왜 Standard Vision Result Schema가 필요한가요?
A. BLIP, Florence-2, Qwen-VL이 서로 다른 출력을 내면 Reference Image Parser와 Character Program이 provider마다 다른 코드를 가져야 합니다. 표준 schema를 두면 caption, character_hints, composition_hints, color_hints를 같은 방식으로 읽을 수 있습니다.

Q. Florence/Qwen은 현재 실제로 연결되어 있나요?
A. 현재는 skeleton adapter입니다. `VLM_PROVIDER=florence` 또는 `VLM_PROVIDER=qwen`을 선택해도 기본 실행 안정성을 위해 BLIP fallback을 사용하고, `used_fallback=true`와 fallback model 이름을 vision_result에 기록합니다.

Q. BLIP fallback을 유지한 이유는 무엇인가요?
A. 무거운 VLM을 필수로 로드하면 로컬 실행성과 데모 안정성이 떨어집니다. 먼저 adapter contract와 schema를 고정하고, 실제 Florence/Qwen 연결은 같은 interface 뒤에 붙일 수 있게 준비했습니다.

Q. vision_result와 caption의 차이는 무엇인가요?
A. caption은 downstream 호환을 위한 짧은 문자열이고, vision_result는 detailed_description, objects, character_hints, style_hints, composition_hints, color_hints, model, provider, fallback 여부를 담는 구조화된 vision context입니다.

## Character Program

Q. 왜 Caption만 사용하지 않았나요?
A. Caption은 이미지 전체를 한 문장으로 요약하기 때문에 identity, outfit, accessories, color, camera composition 같은 보존 단서를 잃기 쉽습니다. Reference Image Parser는 caption을 구조화된 visual context로 바꾸어 Character Program이 더 안정적으로 캐릭터 정보를 사용할 수 있게 합니다.

Q. Reference Image Parser는 어떤 역할을 하나요?
A. VisionAgent가 만든 caption과 vision_result를 읽어 identity, appearance, style, composition, colors, identity rules를 추출합니다. 현재는 rule-based parsing이지만, 향후 Florence/Qwen 같은 VLM 결과를 더 정교하게 받아들일 수 있는 interface 역할을 합니다.

Q. Reference Image Parser와 Character Program의 관계는?
A. Reference Image Parser는 원본 이미지에서 구조적 단서를 뽑는 단계이고, Character Program은 그 단서를 generation context에서 사용할 수 있는 캐릭터 중심 표현으로 정리하는 단계입니다.

Q. Caption과 Character Program의 차이는?
A. Caption은 이미지 내용을 한 문장으로 요약한 텍스트입니다. Character Program은 gender, outfit, accessories, pose, expression, identity rules처럼 캐릭터 보존에 필요한 정보를 구조화한 데이터입니다.

Q. 왜 Character Program을 만들었나요?
A. Style Transfer와 Character Preservation에서는 단순 caption보다 캐릭터 정체성 단서가 중요합니다. Character Program은 Vision Result를 Context Program과 Prompt Compiler가 재사용할 수 있는 구조로 바꿉니다.

Q. Character Program은 Prompt와 어떻게 다른가요?
A. Prompt는 모델 입력 문장이고, Character Program은 prompt 이전 단계의 structured context입니다. Prompt Compiler가 provider별 prompt를 만들 때 필요한 identity 정보를 제공하는 중간 표현입니다.

## Goal-oriented Planning

Q. Goal Tree가 필요한 이유는?
A. Execution plan은 어떤 agent를 실행할지 정하지만, Goal Tree는 무엇을 가장 중요하게 유지할지 정합니다. 예를 들어 anime portrait에서는 identity와 face clarity가 높은 priority가 됩니다.

Q. Prompt보다 Goal을 먼저 만드는 이유는?
A. Prompt를 바로 만들면 style, identity, composition 같은 우선순위가 섞일 수 있습니다. Goal을 먼저 만들면 prompt compiler가 어떤 정보를 더 강하게 반영해야 하는지 알 수 있습니다.

Q. Goal Planning과 Adaptive Planning 차이는?
A. Goal Planning은 생성 전 목표와 priority를 세우는 사전 계획입니다. Adaptive Planning은 평가와 reflection 이후 실패 원인을 보고 다음 시도를 다시 계획하는 loop입니다.

## Adaptive Planning

Q. Retry와 Adaptive Planning의 차이는?
A. Retry는 score threshold를 기준으로 다시 생성할지 결정하는 정책입니다. Adaptive Planning은 그 전에 왜 실패했는지 분석하고, 다음 생성에서 무엇을 바꿀지 전략과 context update를 만드는 re-planning 단계입니다.

Q. 왜 Reflection만으로 끝내지 않았나요?
A. Reflection은 실패 원인을 설명하지만 실행 가능한 planning update로 변환하지는 않습니다. AdaptivePlanner는 reflection을 바탕으로 character priority, layout, style weight, camera framing 같은 변경 사항을 state에 반영합니다.

Q. Adaptive Planning은 무엇을 수정하나요?
A. 현재는 rule 기반으로 context_program의 character preservation rules, layout composition rules, style rendering rules, quality keywords를 보강하고 priority_change를 기록합니다. retry가 필요하면 prompt compiler와 provider adapter가 이 업데이트를 반영합니다.

## Strategy Selection

Q. 왜 CLIP 하나만 쓰지 않았나요?
A. CLIP은 image-text alignment에는 유용하지만 identity preservation, prompt completeness, aesthetic prompt quality를 모두 설명하지는 못합니다. Multi-Metric Evaluation은 여러 관점을 분리해 더 설명 가능한 평가를 만듭니다.

Q. Metric Aggregator를 만든 이유는?
A. 평가 기준을 metric 단위로 분리하면 PickScore, DINO, Aesthetic Score, VLM Judge 같은 새 metric을 쉽게 추가할 수 있습니다. Aggregator는 각 metric을 실행하고 weight 기반 score를 계산합니다.

Q. Metric을 추가하려면 어떻게 하나요?
A. `BaseMetric` 인터페이스를 구현하고 `evaluate(state)`가 `{name, score, reason}`을 반환하게 만든 뒤 `EvaluationAggregator`의 metric list와 weight에 추가하면 됩니다.

Q. Evaluation과 Self Verification의 차이는 무엇인가요?
A. Evaluation은 생성 이미지와 텍스트의 유사도 같은 점수를 계산합니다. Self Verification은 그 점수와 Goal Tree, Context Program, Prompt Report를 함께 보고 목표 충족 여부와 재계획 필요성을 판단합니다.

Q. 왜 Adaptive Planning 전에 Self Verification을 수행하나요?
A. Adaptive Planning은 전략을 바꾸는 단계이므로, 그 전에 현재 결과가 실제로 목표를 만족하지 못했는지 확인해야 합니다. 이렇게 하면 불필요한 retry와 prompt drift를 줄일 수 있습니다.

Q. needs_replanning은 어떻게 판단하나요?
A. best_score가 낮거나, context validation score가 낮거나, prompt missing section 또는 semantic conflict가 있거나, identity priority가 높은데 provider prompt에 preservation language가 부족하면 true가 됩니다.

Q. Self Verification은 Strategy Selector에 어떤 영향을 주나요?
A. needs_replanning이 false이면 StrategySelector가 low-risk strategy를 선택하고, blocking issue가 있으면 해당 issue를 해결하는 전략의 score를 올립니다.

Q. Strategy Selector를 만든 이유는?
A. AdaptivePlanner가 하나의 전략만 만들면 대안 비교가 어렵습니다. StrategySelector는 여러 candidate strategy를 만들고 score로 선택해 의사결정 과정을 설명 가능하게 만듭니다.

Q. Hypothesis와 Strategy의 차이는?
A. Hypothesis는 실패 원인에 대한 가설입니다. Strategy는 그 가설을 바탕으로 다음 generation에서 실제로 바꿀 행동 계획입니다.

Q. Adaptive Planning은 Strategy를 어떻게 활용하나요?
A. AdaptivePlanner는 selected_strategy를 읽어 context_updates와 priority_change를 만들고, ExecutionEngine은 이를 Context Program에 반영한 뒤 prompt compiler를 다시 실행합니다.

## Future Work

- Context Program v2 schema validation
- Docker/FastAPI deployment
- Queue-based generation
- Dashboard and benchmark dashboard
- Multi-session memory
