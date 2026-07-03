# Sprint 39 Design History

## Problem

Prompt orchestration 결과가 많아지면서 `PromptAssembler`가 specialist agent output, memory, retrieval, provider constraint를 한 번에 처리해야 했습니다. 이 구조는 prompt가 길어지고, agent context와 generation prompt가 섞일 위험이 있습니다.

## Decision

`ContextProgramBuilder`를 추가해 provider-independent `context_program`을 만들고, `PromptAssembler`와 `ProviderPromptAdapter`가 이 구조를 참조하도록 변경했습니다.

## Alternatives

- `PromptAssembler` 내부에 context 정리 로직을 계속 추가한다.
- ProviderPromptAdapter가 각 state key를 직접 읽게 한다.
- 모든 prompt 생성을 LLM optimizer에 맡긴다.

## Adopted Reason

Context Program은 agent state를 구조화하는 framework-level intermediate representation입니다. 이 구조를 두면 Context Engineering, Prompt Assembly, Provider Adaptation을 분리할 수 있고, provider가 바뀌어도 specialist agent output을 재사용할 수 있습니다.

## Future Improvement

- Context Program JSON schema 또는 dataclass validation 추가
- provider별 context compiler unit test 추가
- benchmark/debug report에서 `context_program_summary` 비교
- LLM 기반 Context Program reviewer 추가
