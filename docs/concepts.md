# Concepts

## Evaluation Agent

`EvaluationAgent`는 생성 결과를 정량적으로 평가하는 agent입니다. Multi-agent workflow에서 generation 이후 단계에 위치하며, 생성된 이미지가 reference image와 final prompt에 얼마나 잘 맞는지 score로 표현합니다.

현재 버전에서는 실제 CLIP 모델을 로드하지 않고 mock score를 반환합니다. 이 mock score는 generated image file 존재 여부와 prompt 길이를 활용해 deterministic하게 계산됩니다.

향후에는 다음 평가 방식으로 확장할 수 있습니다.

- CLIP similarity: reference image, generated image, prompt 간 semantic similarity 평가
- DINO similarity: 이미지 간 visual feature similarity 평가
- Aesthetic score: 생성 이미지의 미적 품질 평가

이 score는 이후 `ReflectionAgent`가 prompt 개선 제안을 만들고, `RetryAgent`가 재시도 여부를 판단하는 feedback loop의 핵심 입력으로 사용할 수 있습니다.

## Reflection Agent

`ReflectionAgent`는 평가 결과를 바탕으로 실패 원인을 분석하는 agent입니다. Multi-agent workflow에서 evaluation 이후 단계에 위치하며, score가 낮을 때 어떤 방향으로 prompt를 개선해야 하는지 제안합니다.

현재 버전은 rule-based mock reflection입니다. 실제 LLM API를 호출하지 않고, score가 `0.75` 미만이면 개선 문구와 `suggested_prompt`를 반환합니다. score가 `0.75` 이상이면 `"no major revision needed"`를 반환합니다.

향후에는 LLM 기반 reflection으로 확장할 수 있습니다. 예를 들어 generated image, reference image caption, final prompt, evaluation score, memory history를 함께 입력해 더 구체적인 실패 원인과 개선 prompt를 생성할 수 있습니다.

## Retry

`RetryAgent`는 retry decision을 담당하는 agent입니다. 현재는 threshold `0.75`를 기준으로 score가 낮으면 retry가 필요하다고 판단합니다.

이번 Sprint에서는 실제 재생성 loop를 실행하지 않습니다. 대신 `retry_needed` 값을 반환해 다음 Sprint에서 retry loop를 연결할 수 있는 구조를 만듭니다.

## Memory

`Memory`는 agent workflow의 실행 기록을 저장하는 layer입니다. 현재는 `memory/history.json`에 JSON 형태로 기록합니다.

저장 항목은 `caption`, `prompt`, `score`, `reflection`, `retry`, `timestamp`입니다. 향후에는 이 기록을 분석해 prompt 개선, retry 정책, agent 성능 비교에 활용할 수 있습니다.

## Working Memory

Working Memory는 현재 실행 중인 agent context입니다. 이번 프로젝트에서는 orchestrator가 실행 중에 들고 있는 `caption`, `final_prompt`, `score`, `reflection`, `retry_needed` 같은 값이 working memory에 해당합니다.

## Episodic Memory

Episodic Memory는 과거 실행 episode의 기록입니다. `memory/history.json`에 저장되는 각 run record가 episodic memory입니다. 이 기록은 향후 prompt 개선이나 retry 정책 분석에 사용할 수 있습니다.

## State Management

State Management는 agent workflow가 현재 어떤 정보를 가지고 있고, 어떤 단계에서 업데이트되는지 관리하는 방식입니다. `OrchestratorAgent`는 각 agent의 결과를 받아 state를 업데이트하고, 마지막에 `MemoryManager.save_run()`으로 저장합니다.

## Agent Context

Agent Context는 agent가 판단할 때 참고하는 입력 정보입니다. 예를 들어 `ReflectionAgent`는 `caption`, `final_prompt`, `score`를 context로 받아 suggested prompt를 만듭니다.

## Memory Interface

Memory Interface는 memory를 읽고 쓰는 표준 API입니다. 현재 `MemoryManager`는 `load_last_run()`, `save_run()`, `get_history()`, `clear_history()`를 제공합니다.

## Evaluation Loop

Evaluation Loop는 생성 결과를 평가하고, 평가 결과를 바탕으로 다음 행동을 결정하는 구조입니다. Sprint 8에서는 initial generation 이후 score가 낮으면 suggested prompt로 한 번 더 generation과 evaluation을 수행합니다.

## Retry Policy

Retry Policy는 언제 다시 시도할지 정하는 규칙입니다. 현재는 `RetryAgent`가 threshold `0.75` 기준으로 `should_retry(score)`만 판단합니다.

## Self-Improving Agent

Self-Improving Agent는 자신의 결과를 평가하고 개선 방향을 반영해 다음 행동을 조정하는 agent 구조입니다. 현재 프로젝트에서는 `Evaluation -> Reflection -> Retry -> Regeneration` 흐름으로 이를 구현합니다.

## Best Result Selection

Best Result Selection은 initial attempt와 retry attempt 중 더 높은 score를 가진 결과를 최종 결과로 선택하는 단계입니다. 이 선택 결과는 `best_prompt`, `best_score`, `best_output_image_path`로 memory에 저장됩니다.

## Human-in-the-loop Interface

Human-in-the-loop Interface는 사용자가 입력을 제공하고 agent workflow 결과를 직접 확인하는 접점입니다. Sprint 9에서는 Gradio UI가 image input과 user prompt를 받아 multi-agent workflow를 실행합니다.

## Demo-driven Development

Demo-driven Development는 내부 구조가 완성되기 전에 실행 가능한 demo를 먼저 만들어 피드백을 받는 방식입니다. 현재 mock model 상태에서도 UI를 통해 전체 workflow를 확인할 수 있습니다.

## Agent Trace Visualization

Agent Trace Visualization은 어떤 agent가 어떤 순서로 실행됐는지 사용자에게 보여주는 방식입니다. UI는 `agent_trace`를 표시해 Vision, Prompt, Generation, Evaluation, Reflection, Retry, Memory 흐름을 확인할 수 있게 합니다.

## BLIP

BLIP는 Bootstrapping Language-Image Pre-training의 약자로, 이미지와 언어를 함께 다루는 Vision-Language Model입니다. 이 프로젝트에서는 image captioning을 위해 `Salesforce/blip-image-captioning-base`를 사용합니다.

## Image Captioning

Image Captioning은 이미지를 입력받아 자연어 설명(caption)을 생성하는 작업입니다. `VisionAgent`는 업로드된 이미지를 caption으로 변환해 이후 prompt generation 단계에 전달합니다.

## VLM Inference

VLM Inference는 Vision-Language Model을 사용해 이미지와 텍스트 사이의 의미를 추론하는 과정입니다. Sprint 10에서는 BLIP processor와 model을 사용해 caption을 생성합니다.

## Tool-Agent Separation

Tool-Agent Separation은 agent가 역할과 의사결정 흐름을 담당하고, tool이 구체적인 외부 모델 또는 API 호출을 담당하게 나누는 설계입니다. `VisionAgent`는 `BlipTool`을 호출하지만 BLIP 내부 구현은 알지 않습니다.

## Lazy Loading

Lazy Loading은 실제로 필요해지는 시점까지 무거운 리소스 로딩을 미루는 방식입니다. `BlipTool`은 첫 `generate_caption()` 호출 시 `_load_model()`을 통해 BLIP를 로드합니다.

## Text-to-Image Generation

Text-to-Image Generation은 텍스트 prompt를 입력받아 이미지를 생성하는 작업입니다. 이 프로젝트에서는 `GenerationAgent`가 final prompt를 `FluxTool`에 전달해 image path를 반환받습니다.

## Diffusion Inference

Diffusion Inference는 diffusion model이 noise에서 이미지를 점진적으로 생성하는 추론 과정입니다. FLUX는 text-to-image generation을 수행하는 diffusion 계열 모델입니다.

## API-based Model Serving

API-based Model Serving은 로컬에서 모델을 직접 실행하지 않고 외부 API를 통해 inference를 요청하는 방식입니다. Sprint 11에서는 Hugging Face `InferenceClient`로 FLUX generation을 시도합니다.

## Fallback Strategy

Fallback Strategy는 외부 모델 또는 API 실패 시 대체 결과를 반환해 전체 workflow가 멈추지 않도록 하는 설계입니다. `FluxTool`은 token이 없거나 API 실패 시 PIL 기반 mock image를 생성합니다.

## Environment Variable

Environment Variable은 API token 같은 설정 값을 코드 밖에서 주입하는 방식입니다. `HF_TOKEN`은 Hugging Face API 호출에 사용되며 `.env` 또는 시스템 환경변수로 설정할 수 있습니다.

## CLIP

CLIP은 이미지와 텍스트를 같은 embedding space로 매핑하는 multimodal model입니다. 이 프로젝트에서는 generated image와 final prompt의 alignment를 평가하는 데 사용합니다.

## Multimodal Embedding

Multimodal Embedding은 이미지와 텍스트처럼 서로 다른 modality를 같은 벡터 공간에 표현하는 방식입니다. CLIP은 image embedding과 text embedding을 비교할 수 있게 만듭니다.

## Cosine Similarity

Cosine Similarity는 두 벡터의 방향 유사도를 측정합니다. CLIP image embedding과 text embedding의 cosine similarity를 계산해 image-text alignment를 평가합니다.

## Image-Text Similarity

Image-Text Similarity는 이미지가 텍스트 설명과 얼마나 잘 맞는지 평가하는 기준입니다. Sprint 12에서는 `final_prompt`와 generated image 사이의 similarity를 0.0~1.0 score로 변환합니다.

## Model-based Evaluation

Model-based Evaluation은 사람이 직접 평가하지 않고 별도 모델을 사용해 결과 품질을 평가하는 방식입니다. CLIP score는 retry loop와 reflection 판단에 사용할 수 있는 자동 평가 signal입니다.

## Planning Agent

Planning Agent는 사용자 입력과 현재 상황을 보고 어떤 작업 순서가 필요한지 계획하는 agent입니다. 이 프로젝트에서는 `PlannerAgent`가 rule-based 방식으로 execution plan을 생성합니다.

## Execution Plan

Execution Plan은 workflow에서 수행할 단계 목록입니다. 예를 들어 `memory_load`, `vision`, `prompt`, `generation`, `evaluation`, `reflection`, `retry`, `memory_save` 같은 step으로 구성됩니다.

## Task Decomposition

Task Decomposition은 복잡한 요청을 작은 작업 단위로 나누는 과정입니다. Multi-agent workflow에서는 각 step이 전문 agent 또는 manager에 대응됩니다.

## Rule-based Planning

Rule-based Planning은 명시적 조건문으로 plan을 만드는 방식입니다. 현재는 image가 있으면 vision step을 포함하고, prompt가 있으면 prompt step을 포함합니다.

## LLM-based Planning

LLM-based Planning은 LLM이 사용자 요청을 해석해 동적으로 plan을 생성하는 방식입니다. 향후 확장 방향이지만, 현재 Sprint에서는 디버깅 가능한 rule-based planning으로 시작합니다.

## Tool Calling

Tool Calling은 이름이나 schema를 기반으로 특정 기능을 호출하는 구조입니다. 이 프로젝트에서는 `ToolRegistry.call(name, *args, **kwargs)`가 tool calling의 시작점입니다.

## Tool Registry Pattern

Tool Registry Pattern은 callable 객체를 이름으로 등록하고 필요할 때 이름으로 호출하는 패턴입니다. Orchestrator는 구체 객체를 직접 다루기보다 registry를 통해 호출합니다.

## Loose Coupling

Loose Coupling은 모듈 간 의존을 줄이는 설계 원칙입니다. `ToolRegistry`는 Orchestrator와 Agent/Tool 구현 사이의 결합을 줄입니다.

## Dependency Inversion

Dependency Inversion은 상위 정책이 하위 구현에 직접 의존하지 않게 하는 원칙입니다. Orchestrator는 구체 Agent 호출 대신 registry interface에 의존합니다.

## Open-Closed Principle

Open-Closed Principle은 확장에는 열려 있고 수정에는 닫혀 있어야 한다는 원칙입니다. ToolRegistry를 사용하면 새 tool 추가 시 registry 등록만 확장할 수 있습니다.

## Dynamic Tool Selection

Dynamic Tool Selection은 plan이나 context에 따라 실행할 tool을 선택하는 방식입니다. 이번 Sprint에서는 registry 기반 호출만 도입했고, 실제 동적 선택은 향후 과제로 남겼습니다.

## Context Engineering

Context Engineering은 agent가 더 좋은 결정을 내릴 수 있도록 필요한 정보를 선별하고 구성하는 작업입니다. Sprint 17에서는 planner result와 memory의 last run을 prompt generation context로 사용합니다.

## Prompt Context Composition

Prompt Context Composition은 caption, user request, planner reason, previous best prompt 같은 정보를 하나의 prompt 생성 context로 조합하는 과정입니다.

## Context-aware Prompting

Context-aware Prompting은 현재 입력뿐 아니라 이전 실행 결과와 계획 정보를 반영해 prompt를 만드는 방식입니다. 이 프로젝트에서는 `PromptAgent`가 선택적 context dict를 받아 final prompt에 짧게 반영합니다.
## Sprint 18 Concepts

### Prompt Compression

Prompt Compression은 raw context를 그대로 prompt에 넣지 않고, 필요한 의미만 짧은 hint로 바꾸는 과정입니다.

### Context Budget

Context Budget은 agent가 모델에 전달할 수 있는 context의 양을 제한하는 설계 기준입니다. 모든 memory를 넣는 대신 현재 task에 필요한 정보만 선택합니다.

### Token Budget

Token Budget은 모델이 한 번에 처리할 수 있는 입력 길이의 한계입니다. CLIP의 text encoder처럼 짧은 sequence limit을 가진 모델에서는 특히 중요합니다.

### Information Selection

Information Selection은 planner result, memory, retry history 중 final prompt에 실제로 도움이 되는 정보만 고르는 과정입니다.
## Sprint 19 Concepts

### Dynamic Workflow

Dynamic Workflow는 사전에 고정된 순서가 아니라 runtime plan에 따라 실행 순서가 결정되는 workflow입니다.

### Execution Engine

Execution Engine은 planner가 만든 step list를 실제 agent/tool 호출로 변환하는 실행 계층입니다.

### State Machine

State Machine은 현재 실행 상태를 저장하고 step이 진행될 때마다 상태를 갱신하는 구조입니다. 이번 Sprint에서는 `state` dict가 이 역할을 합니다.

### Runtime Dispatch

Runtime Dispatch는 step 이름을 보고 실행 시점에 어떤 tool을 호출할지 결정하는 방식입니다. `ToolRegistry.call(step)`이 이 역할을 합니다.

### Planner-driven Workflow

Planner-driven Workflow는 PlannerAgent가 만든 `execution_plan`이 실제 workflow를 이끄는 구조입니다.

### Agent State

Agent State는 caption, final_prompt, score, reflection, retry result처럼 여러 agent가 공유하는 실행 중간 결과입니다.
## Sprint 20 Concepts

### Knowledge Store

Knowledge Store는 style, lighting, composition, quality, negative prompt rule 같은 domain knowledge를 저장하는 계층입니다.

### Knowledge Layer

Knowledge Layer는 agent가 외부 지식에 접근하는 interface입니다. 이번 Sprint에서는 `KnowledgeManager`가 이 역할을 합니다.

### Retriever

Retriever는 query와 관련된 knowledge를 찾는 component입니다. `RetrievalAgent`는 caption과 user prompt를 기반으로 rule을 검색합니다.

### Rule-based RAG

Rule-based RAG는 embedding이나 Vector DB 없이 keyword matching과 rule selection으로 retrieval-augmented prompt를 만드는 방식입니다.

### Prompt Augmentation

Prompt Augmentation은 검색된 지식을 final prompt 생성에 반영하는 과정입니다. 이번 구조에서는 PromptCompressor가 retrieved context를 짧게 압축해 PromptAgent에 전달합니다.

### Hybrid Retrieval

Hybrid Retrieval은 keyword rule, metadata, vector similarity를 함께 사용하는 retrieval 전략입니다. 향후 확장 방향입니다.
## Sprint 21 Concepts

### Semantic Memory

Semantic Memory는 현재 요청과 의미적으로 유사한 과거 경험이나 지식을 찾아 사용하는 memory입니다. 이번 Sprint에서는 embedding 없이 keyword overlap으로 semantic-like retrieval을 구현했습니다.

### Episodic Memory

Episodic Memory는 과거 실행 단위의 기록입니다. `history.json`의 각 run이 하나의 episode 역할을 합니다.

### Similarity Search

Similarity Search는 query와 memory record 사이의 유사도를 계산해 가장 관련 있는 기록을 찾는 과정입니다.

### Memory-Augmented Agent

Memory-Augmented Agent는 현재 입력뿐 아니라 과거 실행 경험을 참고해 더 나은 결정을 내리는 agent입니다.

### Keyword Similarity

Keyword Similarity는 lowercase, stopword removal, token overlap을 사용해 단순 유사도를 계산하는 방식입니다.

### Future Vector DB Migration

현재 MemoryManager interface를 유지하면 내부 구현을 JSON에서 ChromaDB, FAISS, Milvus로 교체할 수 있습니다.
## Sprint 22 Concepts

### Prompt Orchestration

Prompt Orchestration은 여러 agent가 prompt의 각 부분을 생성하고 조율해 최종 prompt를 만드는 구조입니다.

### Role-based Prompting

Role-based Prompting은 character, style, layout, lighting, negative prompt처럼 prompt 책임을 역할별로 나누는 방식입니다.

### Prompt Assembly

Prompt Assembly는 여러 prompt fragment를 일관된 generation prompt로 결합하는 과정입니다.

### Agent Collaboration

Agent Collaboration은 각 agent가 독립적인 부분 결과를 만들고, 전체 workflow에서 함께 하나의 결과를 완성하는 구조입니다.
## Sprint22 Detailed Concepts

### Prompt Routing

Prompt Routing sends each prompt responsibility to a specialized agent such as CharacterAgent, PoseAgent, or NegativePromptAgent.

### Generation Prompt vs Agent Context

Generation Prompt is the concise image creation instruction. Agent Context includes planner, memory, retrieval, and debug state and should not be copied directly into the image prompt.

### Negative Prompt Separation

Negative Prompt Separation keeps avoid-rules separate from positive image description so future generation providers can receive it as a dedicated field.
## Sprint23 Concepts

### Character Reference Handling

Character Reference Handling treats uploaded images as identity references for one or more characters.

### Identity Preservation

Identity Preservation means keeping recognizable outfit, hairstyle, silhouette, proportions, visual vibe, and color balance.

### Multi-Character Prompting

Multi-Character Prompting structures prompts so multiple characters remain separate and recognizable.

### Character Separation

Character Separation prevents multiple reference images from being merged into a single hybrid character.

### Reference-aware Prompting

Reference-aware Prompting adds explicit rules that generated images should preserve the reference identity.
## Sprint24 Concepts

### Visual Composition Planning

Visual Composition Planning defines how subjects, frames, camera, background, and spacing should be arranged.

### Scene Layout Planning

Scene Layout Planning describes the overall structure of the generated image, including frame type and background style.

### Camera Planning

Camera Planning decides view direction and scale such as eye-level, close-up, medium shot, or full-body view.

### Prompt Layout Design

Prompt Layout Design converts visual structure plans into prompt phrases that image models can follow.
## Sprint25 Concepts

### Scene Planning

Scene Planning interprets user intent as a visual situation before prompt assembly.

### Scene Graph

Scene Graph is a future extension where characters, relationships, actions, and objects are represented as connected nodes.

### Intent Parsing

Intent Parsing extracts scene type, emotion, relationship, interaction, and camera intent from natural language.

### Visual Narrative Planning

Visual Narrative Planning defines what story or moment the generated image should communicate.

### Structured Intermediate Representation

A structured intermediate representation sits between user prompt and generation prompt so downstream agents share the same plan.

### Scene Plan vs Layout Plan

Scene Plan describes what is happening. Layout Plan describes how it is arranged visually.
## Sprint26 Concepts

### Adapter Pattern

Adapter Pattern converts one stable interface into provider-specific formats.

### Canonical Prompt

Canonical Prompt is the provider-neutral generation intent created by PromptAssembler.

### Provider-specific Prompt

Provider-specific Prompt is optimized for one image generation model or provider.

### Model-specific Prompt Optimization

Model-specific Prompt Optimization adjusts length, wording, negative prompt handling, and instruction style for each provider.
## Sprint27 Concepts

### Provider Routing

Provider Routing selects the generation provider based on request intent and provider capability.

### Capability-based Routing

Capability-based Routing chooses a provider based on available model strengths such as negative prompt support or long instruction following.

### Model Selection

Model Selection is the decision layer that chooses which model or provider should handle a task.

### Fallback Provider

Fallback Provider is used when the requested provider is unavailable.

### Routing Policy

Routing Policy is the rule set used to choose requested and selected providers.
## Sprint29 Concepts

### Prompt Critique

Prompt Critique means reviewing a prompt before generation to find structural issues such as duplication, missing sections, unclear composition, or excessive length.

### Self Critique

Self Critique is an agent pattern where the system evaluates its own intermediate output before passing it to the next step. In this project, the prompt is evaluated before provider routing and generation.

### Prompt Validation

Prompt Validation checks whether required prompt sections exist: character, style, layout, pose, expression, lighting, and negative prompt.

### Prompt Diagnostics

Prompt Diagnostics produces a structured report with warnings, suggestions, and a quality score. This makes prompt quality observable instead of hidden inside generation results.
