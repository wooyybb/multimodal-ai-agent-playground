# Sprint 27: Provider Router

## Objective

Rule-based ProviderRouter를 추가해 provider selection을 독립 계층으로 만든다.

## Problem

ProviderPromptAdapter는 provider별 prompt 변환을 할 수 있지만, 어떤 provider를 사용할지 선택하는 계층이 없었다.

## Design Decision

`ProviderRouter`를 추가하고 ExecutionEngine에서 provider adapter 전에 실행한다.

## Implementation Summary

- `agents/provider_router.py` 추가
- Planner execution plan에 `provider_router` 추가
- Orchestrator registry에 `provider_router` 등록
- ExecutionEngine이 `state["provider_routing"]`, `state["provider"]` 저장
- ProviderPromptAdapter가 `state["provider"]`를 사용하도록 변경

## AI Agent Concept

ProviderRouter는 model selection agent다. provider capability와 request intent를 보고 적절한 generation provider를 선택한다.

## Prompt Engineering Note

Prompt routing은 어떤 prompt를 어떻게 변환할지 이전에, 어떤 provider로 보낼지를 결정하는 단계다.

## Interview Talking Points

Q. 현재 FLUX만 쓰는데 ProviderRouter가 왜 필요한가요?
A. 지금은 fallback이지만, 향후 SDXL/GPT Image/Imagen을 붙일 때 선택 책임을 이미 분리해둘 수 있습니다.

## Future Work

- capability config
- provider benchmark
- multi-provider evaluation
