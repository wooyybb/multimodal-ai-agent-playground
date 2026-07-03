# Concepts

## Context Engineering

Context Engineering은 Agent가 사용할 정보를 구조화하는 작업입니다. 이 프로젝트에서는 user prompt, caption, memory, retrieval, scene plan, provider constraint를 Context Program으로 정리합니다.

## Semantic Planning

Semantic Planning은 prompt 이전 단계에서 user intent를 user goal, scene goal, composition goal, interaction goal, style goal, priority로 해석하는 과정입니다. `LLMContextReasoner`는 현재 mock LLM interface로 동작하며 실제 API를 호출하지 않습니다.

## Prompt Engineering

Prompt Engineering은 structured context를 모델 입력 문장으로 변환하는 작업입니다. canonical prompt, provider prompt, evaluation prompt, retry prompt를 분리합니다.

## LLM Prompt Critique

LLM Prompt Critique는 prompt를 직접 수정하지 않고 semantic issue, conflict, priority issue, provider suitability issue를 structured report로 진단하는 단계입니다.

## LLM Provider Abstraction

LLM Provider Abstraction은 Agent가 OpenAI, Gemini, Claude, Ollama 같은 provider를 직접 알지 않도록 `LLMClient`와 `BaseLLM` interface 뒤로 숨기는 구조입니다. 현재 구현체는 `MockLLM`뿐입니다.

## AI Model Service

AIModelService는 LLMClient 아래의 service layer입니다. Agent 요청을 받아 Provider Registry를 통해 Mock/OpenAI/Gemini/Claude/Ollama provider로 위임합니다. 현재 외부 API 호출은 없고 MockProvider만 실제 동작을 담당합니다.

## OpenAI Provider

OpenAIProvider는 AIModelService 아래의 provider implementation입니다. `OPENAI_API_KEY`가 있을 때 OpenAI API 호출을 시도하고, key가 없거나 응답 parsing에 실패하면 MockProvider fallback을 사용합니다.

## Prompt Compiler

Prompt Compiler는 provider-independent Context Program을 provider-specific compiled prompt package로 변환하는 단계입니다. FLUX는 짧고 밀도 높은 positive prompt를 사용하고, SDXL은 positive/negative prompt 분리를 유지하며, GPT Image는 structured instruction block을 유지할 수 있습니다.

## Semantic Prompt Validation

Semantic Prompt Validation은 rule-based 중복/누락 검사를 넘어 user intent, scene goal, layout, style priority가 서로 충돌하지 않는지 확인합니다.

## Conflict Detection

Conflict Detection은 photobooth와 battle scene처럼 동시에 만족하기 어려운 intent 충돌을 찾습니다.

## Hybrid Critic

Hybrid Critic은 deterministic rule-based critic과 mock/future LLM critic을 함께 사용합니다. 안정적인 rule과 semantic reasoning을 분리합니다.

## Provider Suitability Critique

Provider Suitability Critique는 prompt가 FLUX, SDXL, GPT Image 같은 provider 제약에 적합한지 점검합니다.

## Execution Engine

`DynamicExecutionEngine`은 execution plan을 읽고 각 step을 실행합니다. Agent가 많아져도 workflow order를 한 곳에서 관리할 수 있습니다.

## Planner

`PlannerAgent`는 user input을 바탕으로 실행할 step list를 만듭니다. 현재는 rule-based이며, 향후 LLM planner로 확장 가능합니다.

## Provider Routing

`ProviderRouter`는 `config/providers.json`을 읽고 enabled provider와 capability를 기준으로 provider를 선택합니다.

## Benchmark

Benchmark Runner는 여러 prompt를 자동 실행하고 score, retry 여부, provider, debug report path를 저장합니다. Report Generator는 JSON 결과를 Markdown/HTML로 요약합니다.

## Debug Report

Debug Report는 한 run의 state snapshot입니다. `report.json`은 machine-readable이고, `prompt_preview.txt`는 human-readable입니다.

## Retry

Retry는 score가 threshold보다 낮을 때 한 번 더 generation/evaluation을 시도하는 구조입니다. 현재는 안정성을 위해 one-step retry만 사용합니다.

## Reflection

Reflection은 evaluation result를 바탕으로 실패 원인과 suggested prompt를 만드는 단계입니다. 현재는 rule-based이며 향후 LLM reflection으로 확장 가능합니다.

## Memory

Memory는 이전 run의 prompt, score, reflection, retry, output path를 저장합니다. Working Memory는 현재 실행 context이고, Episodic Memory는 과거 실행 기록입니다.

## VLM Adapter

VLM Adapter는 VisionAgent가 특정 vision-language model에 직접 묶이지 않도록 하는 abstraction layer입니다. 현재 기본 provider는 BLIP이고, Florence-2와 Qwen-VL은 skeleton provider로 준비되어 있습니다.

## Vision Provider Abstraction

Vision Provider Abstraction은 `analyze(image, prompt=None) -> dict` 인터페이스를 통해 caption, detailed_description, objects, style_hints, character_hints를 같은 형태로 반환하게 합니다.

## Multimodal Understanding

Multimodal Understanding은 이미지와 텍스트 intent를 함께 해석하는 단계입니다. 현재는 BLIP caption 중심이지만, `vision_result` 구조를 통해 더 자세한 scene/object parsing으로 확장할 수 있습니다.

## Reference Image Understanding

Reference Image Understanding은 업로드된 이미지를 단순 caption이 아니라 character, style, layout reference로 사용하는 방향입니다. Sprint 48은 이 확장을 위한 provider boundary를 먼저 만들었습니다.

## Character Program

Character Program은 caption을 prompt로 바로 쓰지 않고 character identity, appearance, style, pose, expression, dominant colors, identity rules로 구조화한 데이터입니다. Prompt가 아니라 Context Program에 포함되는 structured object이며, Character Preservation과 Style Transfer를 위한 중간 표현입니다.

## Identity Representation

Identity Representation은 gender, estimated age, species, role, outfit, accessories 같은 character consistency 정보를 유지하기 위한 구조입니다. 생성 prompt가 바뀌어도 동일 캐릭터의 핵심 단서를 보존하는 데 사용됩니다.

## Goal-oriented Planning

Goal-oriented Planning은 execution plan을 만들기 전에 "무엇을 해야 하는가"와 "무엇을 가장 중요하게 유지해야 하는가"를 정리하는 단계입니다. Goal Tree는 main goal, sub goals, priorities, success criteria를 포함합니다.

## Goal Tree

Goal Tree는 prompt가 아니라 planning object입니다. identity, style, composition, lighting, background 같은 priority를 구조화해 Context Program과 Prompt Compiler가 더 일관된 선택을 하도록 돕습니다.

## Priority Planning

Priority Planning은 anime, cinematic, portrait 같은 user intent에 따라 identity, style, lighting, composition의 중요도를 조정하는 과정입니다.

## Adaptive Planning

Adaptive Planning은 evaluation과 reflection 이후 다음 generation 전략을 다시 세우는 loop입니다. 단순 Retry는 score만 보고 한 번 더 생성하지만, Adaptive Planner는 failure analysis, hypothesis, strategy, context updates, priority change를 만들어 prompt compiler 이전 context를 보강합니다.

## Re-Planning

Re-Planning은 기존 prompt를 그대로 재사용하지 않고 실패 원인에 맞춰 character priority, layout simplicity, style weight, camera framing 같은 planning 요소를 수정하는 과정입니다.

## Future Work

- Context Program schema validation
- Vector DB memory backend
- LLM planner and LLM reflection
- Benchmark dashboard
