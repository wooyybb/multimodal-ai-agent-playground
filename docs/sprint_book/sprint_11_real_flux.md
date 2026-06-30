# Sprint 11

## Objective

mock generation을 FLUX API 기반 generation 구조로 확장합니다.

## Background

Text-to-image generation 경험을 보여주려면 실제 모델 호출 구조가 필요했습니다.

## Problem

GenerationAgent가 PIL mock image만 생성했습니다.

## Design Decision

`FluxTool`에서 Hugging Face InferenceClient를 사용하고, 실패 시 fallback image를 생성했습니다.

## Architecture

```text
GenerationAgent -> FluxTool -> FLUX API or fallback image
```

## Implementation Summary

환경변수 기반 token 확인, timestamp output path, fallback image를 구현했습니다.

## AI Agent Concept

API-based Model Serving.

## Prompt Engineering Note

보안 정보와 fallback 전략을 명확히 제한했습니다.

## Codex Usage

Codex는 API integration을 tool layer에 한정했습니다.

## Debugging Experience

network/API 실패에도 workflow가 멈추지 않도록 하는 것이 중요했습니다.

## Interview Talking Points

- 예상 질문: FLUX 연동은 어떻게 했나요?
- 예상 답변: GenerationAgent는 FluxTool만 호출하고, FluxTool이 API/fallback을 처리합니다.
- 꼬리 질문: token은 어떻게 관리하나요?

## Lessons Learned

외부 API는 fallback 없이 workflow에 직접 묶으면 위험합니다.

## Future Work

seed, size, batch generation 옵션을 추가합니다.
