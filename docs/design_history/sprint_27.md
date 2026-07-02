# Sprint 27: Provider Router

## Problem

ProviderPromptAdapter가 provider-specific prompt를 만들 수 있었지만 provider 선택은 고정되어 있었다.

## Decision

ProviderRouter를 추가해 user_prompt, scene_plan, planner_result를 기반으로 provider를 선택하도록 했다.

## Alternatives

- `provider="flux"` 고정 유지
- ProviderPromptAdapter 내부에서 provider 선택
- GenerationAgent 내부에서 provider 선택
- LLM-based router 바로 도입

## Reason

provider 선택과 prompt 변환을 분리해야 FLUX, SDXL, GPT Image, Imagen 등 다양한 provider 확장이 쉬워진다.

## Future Work

- Provider capability config
- multi-provider generation
- cost/latency-aware routing
- benchmark-based provider selection
- LLM router
