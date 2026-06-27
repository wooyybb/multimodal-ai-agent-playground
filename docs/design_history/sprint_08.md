# Sprint 8: One-Step Retry Loop

## Problem

Evaluation과 Reflection은 있었지만 결과를 바탕으로 행동을 바꾸는 loop가 없었습니다.

## Decision

score가 threshold보다 낮으면 `suggested_prompt`로 한 번 더 이미지를 생성하고 평가합니다.

## Alternatives

- Retry 없음
- 무한 Retry
- 고정 횟수 Multi-Retry
- LLM Planner 기반 Retry

## Reason

MVP 단계에서는 1회 Retry가 가장 단순하고 디버깅하기 쉽습니다. 무한 retry를 피하면서 reflection-based prompt revision이 실제 workflow에 반영되는지 확인할 수 있습니다.

## Future Work

max_retry_count, dynamic threshold, LLM-based reflection, planner-based retry로 확장합니다.
