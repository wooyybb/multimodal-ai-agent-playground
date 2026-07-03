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

## Future Work

- Context Program schema validation
- Vector DB memory backend
- LLM planner and LLM reflection
- Benchmark dashboard
