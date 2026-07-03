# Interview Notes

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

## Future Work

- Context Program v2 schema validation
- Docker/FastAPI deployment
- Queue-based generation
- Dashboard and benchmark dashboard
- Multi-session memory
