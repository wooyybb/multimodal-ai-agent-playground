# Sprint 26: Provider Prompt Adapter

## Objective

Canonical Prompt와 Provider-specific Prompt를 분리한다.

## Problem

이미지 생성 provider마다 prompt 해석 방식이 다르지만 기존 구조는 PromptAssembler가 만든 prompt를 바로 GenerationAgent에 전달했다.

## Design Decision

`ProviderPromptAdapter`를 추가하고 FLUX adapter를 실제 workflow에 연결했다. GPT Image와 SDXL은 skeleton adapter로 준비했다.

## Implementation Summary

- `agents/provider_prompt_adapter.py` 추가
- `PromptAssembler` 반환값에 `canonical_prompt` 추가
- Planner execution plan에 `provider_prompt_adapter` 추가
- Orchestrator registry에 provider adapter 등록
- ExecutionEngine이 provider prompt를 생성하고 `final_prompt`를 provider prompt로 업데이트

## AI Agent Concept

ProviderPromptAdapter는 canonical generation intent를 각 model/provider가 잘 이해하는 prompt 형식으로 바꾸는 adapter layer다.

## Prompt Engineering Note

Generation prompt와 provider prompt를 분리하면 provider별 prompt length, negative prompt, instruction style을 독립적으로 최적화할 수 있다.

## Interview Talking Points

Q. ProviderPromptAdapter는 왜 필요한가요?
A. FLUX, SDXL, GPT Image는 prompt 해석 방식이 다르기 때문에 canonical prompt를 provider별로 변환해야 합니다.

## Future Work

- Provider routing
- Multi-provider evaluation
- Imagen adapter
