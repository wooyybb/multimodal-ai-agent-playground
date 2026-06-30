# Sprint 04

## Objective

`GenerationAgent`와 `FluxTool`을 연결해 mock image generation을 수행합니다.

## Background

final prompt가 실제 output image로 이어지는 단계가 필요했습니다.

## Problem

실제 FLUX를 바로 붙이면 token, API, GPU 문제가 생길 수 있습니다.

## Design Decision

PIL 기반 fallback/mock image를 먼저 생성했습니다.

## Architecture

```text
PromptAgent -> GenerationAgent -> FluxTool -> output image path
```

## Implementation Summary

`outputs/output_mock.png`를 생성하고 path를 반환했습니다.

## AI Agent Concept

Text-to-Image Generation boundary.

## Prompt Engineering Note

실제 FLUX 호출 금지와 PIL mock image 생성을 명시했습니다.

## Codex Usage

Codex는 image output contract를 구현했습니다.

## Debugging Experience

output path가 downstream evaluation의 중요한 contract임을 확인했습니다.

## Interview Talking Points

- 예상 질문: 왜 mock generation부터 했나요?
- 예상 답변: generation agent의 입출력 계약을 먼저 검증하기 위해서입니다.
- 꼬리 질문: 실제 FLUX로 바꾸면 어디를 수정하나요?

## Lessons Learned

모델 통합 전에도 end-to-end path contract를 만들 수 있습니다.

## Future Work

Hugging Face FLUX API를 연결합니다.
