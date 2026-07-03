# Architecture

## Sprint39: Context Program Layer

현재 구조는 Prompt Specialist Agent가 만든 결과를 바로 긴 generation prompt로 합치는 방식에서 한 단계 더 발전했습니다.

```text
PlannerAgent
-> DynamicExecutionEngine
-> Character / Style / Layout / Pose / Expression / Lighting / Negative Agents
-> ContextProgramBuilder
-> PromptAssembler
-> PromptCritic / PromptOptimizer
-> ProviderRouter
-> ProviderPromptAdapter
-> GenerationAgent
```

`ContextProgramBuilder`는 provider-independent structured context program을 만듭니다. 이 객체는 `task`, `user_goal`, `scene`, `characters`, `style`, `layout`, `pose`, `expression`, `lighting`, `quality`, `negative`, `memory`, `retrieval`, `provider`, `output` 섹션으로 구성됩니다.

중요한 점은 `context_program` 전체를 prompt에 그대로 붙이지 않는다는 것입니다. `PromptAssembler`와 `ProviderPromptAdapter`는 이 구조화된 중간 표현을 읽고, 실제 generation prompt에는 subject, style, layout, lighting, pose, expression처럼 provider가 이해할 수 있는 visual instruction만 컴파일합니다.

이 레이어를 추가한 이유는 Context Engineering과 Prompt Engineering을 분리하기 위해서입니다. Context Program은 agent state를 정리하는 framework-level intermediate representation이고, ProviderPromptAdapter는 이를 FLUX, GPT Image, SDXL 같은 provider별 prompt 형식으로 변환합니다.

이 프로젝트는 단일 파이프라인(Single Pipeline)에서 멀티 에이전트 아키텍처(Multi-Agent Architecture)로 발전 중입니다.

## Current Structure

```text
User -> OrchestratorAgent
├── MemoryManager(load)
├── VisionAgent
├── PromptAgent
├── GenerationAgent
├── EvaluationAgent
├── ReflectionAgent
├── RetryAgent
└── MemoryManager(save)
```

현재 버전은 사용자의 이미지 입력과 텍스트 요청을 받아 `OrchestratorAgent`가 전체 workflow를 조율합니다. 시작 시 `MemoryManager`가 마지막 실행 기록을 load하고, 이후 `VisionAgent`, `PromptAgent`, `GenerationAgent`, `EvaluationAgent`, `ReflectionAgent`, `RetryAgent`가 순서대로 실행됩니다. 마지막으로 `MemoryManager`가 현재 실행 기록을 `memory/history.json`에 save합니다. Memory 접근은 `OrchestratorAgent`로 제한해 개별 agent가 저장소 구조에 직접 의존하지 않도록 설계했습니다.

## Future Structure

```text
User -> OrchestratorAgent -> VisionAgent -> PromptAgent -> GenerationAgent -> EvaluationAgent -> ReflectionAgent -> RetryAgent -> Memory
```

향후 버전에서는 실제 재생성 loop와 LLM 기반 reflection을 연결할 예정입니다.

## Agent Roles

- `OrchestratorAgent`: 전체 multi-agent workflow를 조율하는 중앙 조정자(coordinator)입니다.
- `VisionAgent`: 이미지에서 caption을 추출하는 vision 담당 agent입니다. 현재는 mock BLIP tool을 사용합니다.
- `PromptAgent`: caption과 user prompt를 조합해 image generation용 final prompt를 생성합니다.
- `GenerationAgent`: final prompt를 기반으로 mock image를 생성합니다. 현재는 실제 FLUX가 아니라 PIL을 사용합니다.
- `EvaluationAgent`: 생성된 이미지와 prompt의 품질을 평가합니다. 현재는 실제 CLIP이 아니라 deterministic mock score를 반환합니다.
- `ReflectionAgent`: 평가 score와 prompt를 바탕으로 개선 제안과 suggested prompt를 생성합니다. 현재는 rule-based mock reflection입니다.
- `RetryAgent`: 평가 score가 threshold보다 낮은지 판단해 retry 여부를 반환합니다. 아직 실제 재생성 loop는 실행하지 않습니다.
- `MemoryManager`: working memory와 episodic memory의 시작점입니다. `load_last_run()`, `save_run()`, `get_history()`, `clear_history()` interface를 제공합니다.

## One-Step Retry Loop

Sprint 8에서는 one-step retry loop를 추가했습니다. `EvaluationAgent`가 initial score를 만들고, `ReflectionAgent`가 suggested prompt를 제안한 뒤, `RetryAgent`가 retry 여부를 판단합니다.

```text
GenerationAgent(initial_prompt)
-> EvaluationAgent(initial_score)
-> ReflectionAgent(suggested_prompt)
-> RetryAgent(should_retry)
-> if retry_needed:
     GenerationAgent(suggested_prompt)
     EvaluationAgent(retry_score)
-> best result selection
-> MemoryManager(save)
```

무한 반복을 피하기 위해 retry는 최대 1회만 수행합니다. `OrchestratorAgent`가 loop를 제어하고, `RetryAgent`는 `should_retry(score)` 판단만 담당합니다.

## Gradio UI Integration

Sprint 9에서는 Gradio UI를 `MultimodalPipeline`에 연결했습니다. UI는 agent를 직접 호출하지 않고 pipeline만 호출합니다.

```text
User
-> Gradio UI
-> MultimodalPipeline
-> OrchestratorAgent
-> VisionAgent
-> PromptAgent
-> GenerationAgent
-> EvaluationAgent
-> ReflectionAgent
-> RetryAgent
-> MemoryManager
-> Gradio UI Output
```

이 구조는 UI와 agent workflow 책임을 분리합니다. UI는 image input, user prompt, result visualization, agent trace display에 집중하고, 실행 순서와 retry loop는 `OrchestratorAgent`가 관리합니다.

## Real BLIP Captioning

Sprint 10에서는 mock caption을 실제 BLIP 기반 image captioning으로 교체했습니다.

```text
VisionAgent
-> BlipTool
-> Salesforce/blip-image-captioning-base
-> Real BLIP Caption
```

`VisionAgent`는 model loading이나 inference details를 알지 않습니다. 실제 BLIP processor/model loading, PIL image 변환, torch inference, fallback caption 처리는 `BlipTool`이 담당합니다.

## Real FLUX Generation

Sprint 11에서는 `GenerationAgent`가 `FluxTool`을 통해 real FLUX generation을 시도하도록 확장했습니다.

```text
PromptAgent
-> GenerationAgent
-> FluxTool
   -> Real FLUX generation if HF_TOKEN exists
   -> Mock fallback image if token is missing or generation fails
```

`GenerationAgent`는 Hugging Face API details를 알지 않습니다. `FluxTool`이 `HF_TOKEN`, `InferenceClient`, image saving, fallback generation을 담당합니다.

## Real CLIP Evaluation

Sprint 12에서는 mock score를 실제 CLIP 기반 image-text similarity score로 확장했습니다.

```text
GenerationAgent
-> EvaluationAgent
-> ClipTool
-> openai/clip-vit-base-patch32
-> image-text similarity score
```

`EvaluationAgent`는 CLIP model internals를 알지 않습니다. `ClipTool`이 processor/model lazy loading, generated image loading, text embedding, image embedding, cosine similarity calculation, fallback score를 담당합니다.

## Current E2E Workflow

Sprint 13 기준 전체 End-to-End workflow는 다음과 같습니다.

```text
User
-> Gradio UI
-> MultimodalPipeline
-> OrchestratorAgent
-> VisionAgent / BLIP
-> PromptAgent
-> GenerationAgent / FLUX or fallback
-> EvaluationAgent / CLIP
-> ReflectionAgent
-> RetryAgent
-> MemoryManager
-> UI Output
```

이번 Sprint에서는 새 agent를 추가하지 않고, UI output stability, agent trace formatting, memory save failure handling, testing documentation을 정리했습니다.

## PlannerAgent

Sprint 15에서는 `OrchestratorAgent` 시작 단계에 `PlannerAgent`를 추가했습니다.

```text
User
-> OrchestratorAgent
-> PlannerAgent
-> Execution Plan
-> Existing Fixed Workflow
```

현재 `PlannerAgent`는 rule-based planner입니다. `image_provided`와 `user_prompt`를 기준으로 `execution_plan`, `task_type`, `reason`을 생성합니다. 이번 Sprint에서는 계획을 실제 dynamic execution engine으로 실행하지 않고, 기존 workflow를 유지하면서 plan을 기록합니다.

## ToolRegistry

Sprint 16에서는 `OrchestratorAgent`와 각 Agent 호출 사이에 `ToolRegistry`를 추가했습니다.

```text
PlannerAgent
-> Execution Plan
-> OrchestratorAgent
-> ToolRegistry
   -> memory_load
   -> vision
   -> prompt
   -> generation
   -> evaluation
   -> reflection
   -> retry
   -> memory_save
```

이번 Sprint의 목표는 완전한 dynamic execution engine이 아니라 registry 기반 호출 구조를 도입하는 것입니다. Orchestrator는 기존 workflow 순서를 유지하지만 각 단계 호출을 `registry.call(...)`로 감싸 Agent/Tool 호출 책임을 중앙화했습니다.

## Context-aware PromptAgent

Sprint 17에서는 `PromptAgent`가 caption과 user prompt뿐 아니라 context dict를 선택적으로 받을 수 있도록 확장했습니다.

```text
MemoryManager.load_last_run()
-> last_run context
PlannerAgent
-> planner_result
VisionAgent
-> caption
OrchestratorAgent
-> context dict
PromptAgent
-> context-aware final_prompt
```

`PromptAgent`는 MemoryManager나 PlannerAgent를 직접 호출하지 않습니다. `OrchestratorAgent`가 `planner_result`, `last_run`, `previous_best_prompt`, `previous_best_score`를 모아 context를 구성하고 `PromptAgent`에 전달합니다.
## Prompt Compression

Sprint 18에서는 Context-aware PromptAgent 앞에 `PromptCompressor`를 추가했습니다.

```text
PlannerAgent
-> Context Builder
-> PromptCompressor
-> Compressed Context
-> PromptAgent
-> GenerationAgent
-> EvaluationAgent
```

`Context Builder`는 Planner와 Memory에서 raw context를 수집하고, `PromptCompressor`는 이 context를 짧은 hint로 압축합니다. `PromptAgent`는 raw planner result, full history, previous best prompt 전체를 직접 사용하지 않고 `compressed_context`만 사용합니다. 이 구조는 CLIP 77 token 제한과 같은 context budget 문제를 줄이고, 향후 RAG Style Library나 Semantic Memory가 추가되어도 prompt 길이를 제어할 수 있게 합니다.
## Dynamic Execution Engine

Sprint 19에서는 PlannerAgent가 만든 `execution_plan`을 실제 실행에 반영하기 위해 `DynamicExecutionEngine`을 추가했습니다.

```text
User
-> PlannerAgent
-> execution_plan
-> OrchestratorAgent
-> DynamicExecutionEngine
-> ToolRegistry.call(step)
-> Agent / Tool execution
```

`OrchestratorAgent`는 더 이상 각 step을 직접 실행하지 않습니다. 대신 초기 `state`를 만들고 `DynamicExecutionEngine.run(execution_plan, registry, state)`를 호출합니다. ExecutionEngine은 step별로 필요한 입력을 state에서 꺼내고, 실행 결과를 다시 state에 저장합니다.

지원 step은 `memory_load`, `vision`, `prompt_compressor`, `prompt`, `generation`, `evaluation`, `reflection`, `retry`, `memory_save`입니다. 이 구조는 향후 caption-only mode, generation-only mode, RAG branch, semantic memory branch 같은 조건부 workflow로 확장하기 위한 기반입니다.
## Knowledge Layer

Sprint 20에서는 Prompt 생성 과정에 rule-based knowledge retrieval을 추가했습니다.

```text
PlannerAgent
-> ExecutionEngine
-> ToolRegistry
-> RetrievalAgent
-> KnowledgeManager
-> knowledge/*.json
-> PromptCompressor
-> PromptAgent
-> GenerationAgent
```

`KnowledgeManager`는 JSON Knowledge Store를 로드하는 interface입니다. `RetrievalAgent`는 caption과 user prompt를 분석해 style, lighting, composition, quality, negative prompt rule을 검색합니다. 검색된 결과는 `retrieved_context`로 state에 저장되고, `PromptCompressor`가 중요한 keyword만 `compressed_context`에 병합합니다.

이번 Sprint에서는 Vector DB를 사용하지 않습니다. RAG의 핵심인 Retrieval과 Augmentation 책임 분리를 먼저 구현하고, 향후 ChromaDB, FAISS, Milvus 같은 storage layer로 확장할 수 있게 설계했습니다.
## Semantic-like Memory Retrieval

Sprint 21에서는 `MemoryManager`를 단순 저장소에서 검색 가능한 memory layer로 확장했습니다.

```text
VisionAgent
-> caption
-> MemoryManager.search_similar_runs(caption + user_prompt)
-> memory_context
-> PromptCompressor
-> PromptAgent
```

`memory_retrieval` step은 `vision` 이후에 실행됩니다. caption이 생성된 뒤에야 현재 이미지 내용과 user prompt를 결합한 query를 만들 수 있기 때문입니다. 검색 결과는 full history가 아니라 `memory_hint`, `memory_score`, `best_run` 요약 신호로 `PromptCompressor`에 전달됩니다.

현재는 Vector DB 없이 JSON history 기반 keyword similarity를 사용합니다. 향후 ChromaDB, FAISS, embedding search로 교체할 수 있도록 `MemoryManager.get_memory_context()` interface를 별도로 유지합니다.
## Prompt Orchestration Framework

Sprint 22에서는 단일 `PromptAgent` 중심 구조를 여러 전문 prompt agent가 협업하는 Prompt Orchestration Framework로 확장했습니다.

```text
Planner
-> ExecutionEngine
-> ToolRegistry
-> CharacterAgent
-> StyleAgent
-> LayoutAgent
-> LightingAgent
-> NegativePromptAgent
-> PromptAssembler
-> GenerationAgent
```

각 agent는 prompt의 한 영역만 담당합니다. `CharacterAgent`는 캐릭터 특징, `StyleAgent`는 style keyword, `LayoutAgent`는 layout, `LightingAgent`는 lighting, `NegativePromptAgent`는 negative prompt를 생성합니다. `PromptAssembler`는 이 fragment를 받아 generation prompt만 조립합니다.
## Sprint22 Detailed Prompt Orchestration Update

Sprint22 detailed version adds `PoseAgent` and `ExpressionAgent` in addition to Character, Style, Layout, Lighting, NegativePrompt, and PromptAssembler.

```text
CharacterAgent
-> StyleAgent
-> LayoutAgent
-> PoseAgent
-> ExpressionAgent
-> LightingAgent
-> NegativePromptAgent
-> PromptAssembler
```

`PromptAssembler` returns `generation_prompt`, `negative_prompt`, and `prompt_sections`. Agent context, planner debug, memory debug, and retrieval debug are not copied directly into the generation prompt.
## Sprint23 Character Reference Handling

Sprint23 extends the prompt orchestration framework with character reference handling.

```text
Reference images or character_inputs
-> CharacterAgent
-> character_count / characters / global_character_rules
-> PromptAssembler
-> generation_prompt with identity preservation rules
```

Each uploaded image is treated as one separate character. The system does not merge characters and adds compact preservation rules for outfit, hairstyle, silhouette, proportions, visual vibe, and color balance.
## Sprint24 Layout Planning

Sprint24 upgrades `LayoutAgent` from keyword generation to composition planning.

```text
User intent
-> LayoutAgent
-> Layout Plan
-> PromptAssembler
-> Generation Prompt
```

The Layout Plan includes `layout_type`, `aspect_ratio`, `frame_structure`, `camera_view`, `subject_placement`, `background_style`, and `composition_rules`. PromptAssembler converts this plan into image-generation prompt phrases instead of copying raw keywords.
## Sprint25 Scene Planning

Sprint25 adds `ScenePlanningAgent` between Planner and prompt section agents.

```text
User Prompt
-> PlannerAgent
-> ScenePlanningAgent
-> Scene Plan
-> LayoutAgent / PoseAgent / ExpressionAgent
-> PromptAssembler
```

The Scene Plan captures `scene_type`, `emotion`, `relationship`, `interaction`, `energy`, `narrative`, `camera_intent`, `scene_rules`, and `avoid`. Downstream agents use this plan without copying the full structure into the prompt.
## Sprint26 Provider Prompt Adapter

Sprint26 separates canonical prompt from provider-specific prompt.

```text
PromptAssembler
-> canonical_prompt
-> ProviderPromptAdapter
-> provider_prompt
-> GenerationAgent
```

The current workflow uses the FLUX adapter. GPT Image and SDXL adapters are skeletons. GenerationAgent interface remains unchanged; ExecutionEngine updates `final_prompt` with `provider_prompt`.
## Sprint27 Provider Router

Sprint27 adds provider selection before provider prompt adaptation.

```text
Planner / ScenePlan / UserPrompt
-> ProviderRouter
-> selected_provider
-> ProviderPromptAdapter
-> GenerationAgent
```

Currently only FLUX is available, so unsupported requested providers fall back to `flux`.

## Sprint28 Provider Capability Config

Sprint28 adds a config layer for provider capabilities.

```text
config/providers.json
-> ProviderRouter
-> selected_provider
-> ProviderPromptAdapter
-> GenerationAgent
```

Provider information is no longer hardcoded inside `ProviderRouter`. The router loads `default_provider`, enabled providers, display names, and capability flags from `config/providers.json`. Only providers with `enabled: true` are selectable. The current workflow keeps FLUX as the default and enabled provider.

## Sprint29 Prompt Critic Agent

Sprint29 adds a prompt validation layer before provider routing.

```text
PromptAssembler
-> PromptCriticAgent
-> ProviderRouter
-> ProviderPromptAdapter
-> GenerationAgent
```

`PromptCriticAgent` does not generate images. It reviews the canonical prompt and reports duplicated keywords, missing prompt sections, prompt length warnings, a rule-based quality score, and improvement suggestions. The generation workflow continues even if the critic fails.

## Sprint30A Standard Agent Interface

Sprint30A starts an incremental move toward a standard Agent interface.

```text
Agent.run(state: dict) -> dict
ExecutionEngine
-> registry.run_with_state(step, state)
-> state.update(result)
```

Only selected upper-layer agents use the new state-based interface in this Sprint: `ScenePlanningAgent`, `PromptAssembler`, `PromptCriticAgent`, `ProviderRouter`, and `ProviderPromptAdapter`. Lower-level BLIP/FLUX/CLIP, retry, memory, and UI flows keep their existing interfaces for backward compatibility.

## Sprint31 Prompt Optimizer Agent

Sprint31 adds a rule-based optimization step after prompt critique.

```text
PromptAssembler
-> PromptCriticAgent
-> PromptOptimizerAgent
-> ProviderRouter
-> ProviderPromptAdapter
-> GenerationAgent
```

`PromptOptimizerAgent` reads `prompt_report`, removes duplicate phrases and internal context terms, repairs missing sections with compact keywords, controls prompt length, and writes the optimized prompt back to `canonical_prompt` and `final_prompt`.

## Sprint32 Intelligent Prompt Optimizer

Sprint32 upgrades PromptOptimizerAgent from broad rule-based cleanup to report-driven optimization.

```text
PromptCriticAgent
-> prompt_report
-> reasoning
-> PromptOptimizerAgent
-> optimized_prompt
-> ProviderPromptAdapter
-> GenerationAgent
```

The optimizer now reads duplicate keywords, missing sections, warnings, and prompt quality score before editing. It performs only the repairs requested by the critic report and prints a Prompt Preview immediately before generation.

## Sprint33 LLM Prompt Optimizer Interface

Sprint33 adds an optional LLM optimization interface after the rule-based optimizer.

```text
PromptAssembler
-> PromptCriticAgent
-> PromptOptimizerAgent
-> LLMPromptOptimizerAgent
   -> disabled/mock/future llm mode
-> ProviderRouter
-> ProviderPromptAdapter
-> GenerationAgent
```

The current implementation does not call an external LLM API. Disabled mode keeps the existing optimized prompt, mock mode performs deterministic local cleanup, and future LLM mode is represented as a safe fallback interface.

## Sprint34 AgentState Framework Core

Sprint34 introduces `AgentState` as the framework-level shared state object.

```text
ExecutionEngine
-> AgentState.from_dict()
-> validate()
-> dict-compatible workflow
-> AgentState.from_dict()
-> to_dict()
```

The existing Agent code still receives dict-style state in this Sprint. `AgentState` acts as a framework core boundary that centralizes common fields, supports validation warnings, preserves unknown keys in `extra`, and keeps the current workflow compatible.

## Sprint35 FastAPI Service Layer

Sprint35 adds a REST service layer without changing the AI Agent framework.

```text
Gradio UI
-> ExecutionEngine
-> Agents

FastAPI
-> REST API
-> Service Layer
-> OrchestratorAgent
-> ExecutionEngine
-> Agents
```

FastAPI exposes `GET /`, `GET /health`, and `POST /generate`. Swagger UI is available at `/docs` and ReDoc at `/redoc`.

## Sprint36 Observability / Debug Report Layer

Sprint36 adds a best-effort debug report layer after generation, retry, and memory preparation.

```text
ExecutionEngine
-> DebugReportManager
-> outputs/runs/run_YYYYMMDD_HHMMSS/
   -> report.json
   -> prompt_preview.txt
   -> initial.png / retry.png / best.png
```

The debug report captures prompt lifecycle artifacts: scene plan, prompt sections, critic report, optimizer report, provider prompt, evaluation prompt, scores, retry result, and agent trace. Report failures do not fail the workflow.
