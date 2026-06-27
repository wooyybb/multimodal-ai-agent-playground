# Sprint 11: Real FLUX Integration

## Problem

`GenerationAgent`가 mock image만 생성하여 실제 text-to-image generation 경험을 보여주기 어려웠습니다.

## Decision

`FluxTool`에 Hugging Face `InferenceClient` 기반 FLUX generation 구조를 추가합니다.

## Alternatives

- Mock generation 유지
- Local diffusers 기반 FLUX 실행
- Stable Diffusion XL 사용
- 외부 이미지 생성 API 사용

## Reason

MVP 단계에서는 API 기반 FLUX 연동이 가장 빠르고 로컬 GPU 의존성을 줄일 수 있습니다.

## Future Work

Local diffusers inference, SDXL fallback, batch generation, seed control, image-to-image generation으로 확장할 수 있습니다.
