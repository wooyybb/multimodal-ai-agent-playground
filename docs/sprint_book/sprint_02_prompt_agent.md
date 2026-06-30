# Sprint 02

## Objective

caption과 user prompt를 조합해 final prompt를 생성합니다.

## Background

이미지 생성 모델은 caption만보다 사용자의 의도를 반영한 prompt가 필요합니다.

## Problem

caption과 user prompt를 어디서 결합할지 책임 경계가 필요했습니다.

## Design Decision

`PromptAgent`를 별도 agent로 두고 prompt composition을 담당하게 했습니다.

## Architecture

```text
caption + user_prompt -> PromptAgent -> final_prompt
```

## Implementation Summary

빈 user prompt도 처리하고, final prompt 로그를 추가했습니다.

## AI Agent Concept

Prompt Engineering Agent.

## Prompt Engineering Note

빈 입력 처리와 출력 예시를 prompt에 명시했습니다.

## Codex Usage

Codex는 문자열 조합 규칙과 logging을 구현했습니다.

## Debugging Experience

빈 prompt 케이스를 별도로 검증했습니다.

## Interview Talking Points

- 예상 질문: PromptAgent를 분리한 이유는?
- 예상 답변: prompt 생성 책임을 독립시켜 나중에 LLM prompt optimizer로 확장하기 위해서입니다.
- 꼬리 질문: 어떤 개선이 가능하나요?

## Lessons Learned

작은 문자열 조합도 agent responsibility로 분리하면 확장성이 좋아집니다.

## Future Work

LLM 기반 prompt refinement로 확장합니다.
