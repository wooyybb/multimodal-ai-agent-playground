# Prompt Archive 022: Multi-Agent Prompt Orchestration

## Purpose

이번 prompt는 prompt engineering을 단일 PromptAgent가 아니라 여러 role-based agent가 협업하는 구조로 확장하기 위한 architecture prompt다.

## Summary

CharacterAgent, StyleAgent, LayoutAgent, LightingAgent, NegativePromptAgent, PromptAssembler를 추가하고 ExecutionEngine이 이 순서대로 실행하도록 구성했다.

## Constraints

- Generation, Vision, Evaluation, Reflection, Retry agent 수정 금지
- memory, ui, main, requirements, README 수정 금지
- 기존 E2E workflow 유지
- Generation Prompt만 assemble하고 agent context 전체는 prompt에 넣지 않기

## Prompt Engineering Note

이번 prompt는 Prompt Routing과 Prompt Assembly 책임을 명확히 분리하도록 설계되었다.
## Detailed Update

The detailed Sprint22 prompt required section outputs as dictionaries and added PoseAgent / ExpressionAgent. PromptAssembler now returns a structured dict instead of a plain string.
