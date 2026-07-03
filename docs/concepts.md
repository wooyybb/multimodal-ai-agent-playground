# Concepts

## Context Engineering

Context Engineering은 Agent가 사용할 정보를 구조화하는 작업입니다. 이 프로젝트에서는 user prompt, caption, memory, retrieval, scene plan, provider constraint를 Context Program으로 정리합니다.

## Semantic Planning

Semantic Planning은 prompt 이전 단계에서 user intent를 user goal, scene goal, composition goal, interaction goal, style goal, priority로 해석하는 과정입니다. `LLMContextReasoner`는 현재 mock LLM interface로 동작하며 실제 API를 호출하지 않습니다.

## Prompt Engineering

Prompt Engineering은 structured context를 모델 입력 문장으로 변환하는 작업입니다. canonical prompt, provider prompt, evaluation prompt, retry prompt를 분리합니다.

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
