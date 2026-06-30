# Sprint 06

## Objective

score 기반 reflection과 retry decision을 추가합니다.

## Background

평가 결과가 낮을 때 개선 방향을 제안해야 self-improving agent 구조가 됩니다.

## Problem

score만으로는 무엇을 개선해야 하는지 알기 어렵습니다.

## Design Decision

`ReflectionAgent`는 suggested prompt를 만들고, `RetryAgent`는 threshold 기반 retry 여부만 판단하게 했습니다.

## Architecture

```text
EvaluationAgent -> ReflectionAgent -> RetryAgent
```

## Implementation Summary

threshold 0.75 기준으로 retry 여부와 suggested_prompt를 반환했습니다.

## AI Agent Concept

Reflection-based Self Improvement.

## Prompt Engineering Note

실제 재생성 loop는 금지하고 decision signal만 반환하도록 제약했습니다.

## Codex Usage

Codex는 reflection/retry 책임 분리를 구현했습니다.

## Debugging Experience

Reflection과 Retry를 분리해야 정책 변경이 쉬워집니다.

## Interview Talking Points

- 예상 질문: RetryAgent가 직접 재생성하지 않는 이유는?
- 예상 답변: RetryAgent는 policy decision만 담당하고 실행은 Orchestrator가 담당해야 합니다.
- 꼬리 질문: threshold는 어떻게 정하나요?

## Lessons Learned

feedback loop는 analysis와 decision을 분리해야 설명하기 쉽습니다.

## Future Work

실제 one-step retry loop를 구현합니다.
