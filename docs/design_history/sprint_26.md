# Sprint 26: Provider Prompt Adapter

## Problem

PromptAssembler가 생성한 prompt가 특정 provider에 직접 연결되어 있어 모델별 prompt 최적화가 어려웠다.

## Decision

Canonical Prompt와 Provider-specific Prompt를 분리하고 `ProviderPromptAdapter`를 도입했다.

## Alternatives

- PromptAssembler에서 provider별 prompt 직접 생성
- GenerationAgent에서 prompt 수정
- 긴 prompt를 그대로 FLUX에 전달
- 모델별 별도 PromptAgent 생성

## Reason

Adapter Pattern을 사용하면 상위 agent 구조를 유지하면서 FLUX, SDXL, GPT Image, Imagen 등 provider별 prompt 전략을 독립적으로 확장할 수 있다.

## Future Work

- Provider Routing
- Multi-provider generation
- provider-specific negative prompt handling
- provider별 evaluation strategy
