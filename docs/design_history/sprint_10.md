# Sprint 10: Real BLIP Integration

## Problem

`VisionAgent`가 mock caption만 반환하여 실제 VLM inference 경험을 보여주기 어려웠습니다.

## Decision

`Salesforce/blip-image-captioning-base`를 `BlipTool`에 통합합니다.

## Alternatives

- Mock caption 유지
- LLaVA 사용
- BLIP-2 사용
- 외부 VLM API 사용

## Reason

BLIP base는 비교적 가볍고 image captioning MVP에 적합합니다. 또한 Hugging Face transformers를 통해 표준적인 방식으로 사용할 수 있습니다.

## Future Work

BLIP-2, LLaVA, GPT-4o Vision 등으로 확장할 수 있습니다.
