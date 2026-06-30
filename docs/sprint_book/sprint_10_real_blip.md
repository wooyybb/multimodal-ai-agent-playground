# Sprint 10

## Objective

mock caption을 실제 BLIP image captioning으로 교체합니다.

## Background

경험기술서와 코드가 일치하려면 실제 VLM inference 구조가 필요했습니다.

## Problem

VisionAgent가 mock caption만 반환했습니다.

## Design Decision

BLIP model loading과 inference를 `BlipTool`에 격리했습니다.

## Architecture

```text
VisionAgent -> BlipTool -> Salesforce/blip-image-captioning-base
```

## Implementation Summary

lazy loading, RGB conversion, fallback caption을 구현했습니다.

## AI Agent Concept

Vision-Language Model Inference.

## Prompt Engineering Note

fallback과 lazy loading을 명시해 모델 통합 위험을 줄였습니다.

## Codex Usage

Codex는 실제 모델 통합을 tool layer에 제한했습니다.

## Debugging Experience

모델 다운로드/캐시 실패를 fallback으로 처리해야 workflow가 유지됩니다.

## Interview Talking Points

- 예상 질문: BLIP는 어떤 역할인가요?
- 예상 답변: 이미지를 caption으로 변환해 prompt generation에 전달합니다.
- 꼬리 질문: VisionAgent와 BlipTool을 왜 나눴나요?

## Lessons Learned

실제 모델 통합은 lazy loading과 fallback이 필수입니다.

## Future Work

BLIP-2, LLaVA, GPT-4o Vision으로 확장합니다.
