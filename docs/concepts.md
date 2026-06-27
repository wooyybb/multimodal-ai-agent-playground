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
