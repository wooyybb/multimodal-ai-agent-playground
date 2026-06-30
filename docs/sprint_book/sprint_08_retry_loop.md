# Sprint 08

## Objective

score가 낮을 때 suggested prompt로 한 번 더 생성/평가하는 one-step retry loop를 구현합니다.

## Background

Reflection과 Retry decision만으로는 행동 변화가 없습니다.

## Problem

agent가 평가 결과를 바탕으로 실제 second attempt를 수행하지 않았습니다.

## Design Decision

retry는 최대 1회로 제한하고 Orchestrator가 loop를 제어하게 했습니다.

## Architecture

```text
Initial Generation -> Evaluation -> Reflection -> Retry Decision -> Optional Second Attempt -> Best Result
```

## Implementation Summary

initial/retry/best result를 memory에 저장했습니다.

## AI Agent Concept

Evaluation Loop and Retry Policy.

## Prompt Engineering Note

무한 loop 방지를 위해 one-step retry를 명시했습니다.

## Codex Usage

Codex는 retry true/false 흐름과 best result selection을 구현했습니다.

## Debugging Experience

retry path 검증에는 stub score가 유용했습니다.

## Interview Talking Points

- 예상 질문: 왜 1회 retry인가요?
- 예상 답변: MVP에서는 무한 loop보다 디버깅 가능한 제어가 중요합니다.
- 꼬리 질문: 다음에는 어떻게 확장하나요?

## Lessons Learned

retry loop는 종료 조건과 기록 schema가 중요합니다.

## Future Work

max retry count와 dynamic threshold를 도입합니다.
