# Sprint 23: Character Reference Handling

## Problem

기존 시스템은 single image caption 중심이라 여러 reference image를 별도 character로 취급하는 구조가 부족했다.

## Decision

`CharacterAgent`에 multi-character schema를 추가하고, `PromptAssembler`가 character preservation rules를 generation prompt에 반영하도록 확장했다.

## Alternatives

- UI에서만 다중 이미지 처리
- PromptAgent에 긴 character rule 직접 추가
- LLM으로 character analysis 전체 처리
- 기존 single-character 구조 유지

## Reason

Schema-first 접근을 통해 multi-image UI와 model integration 전에 multi-character prompting 구조를 안정적으로 만들 수 있다.

## Future Work

- Multi-image UI
- per-character VLM analysis
- identity similarity evaluation
- mask/reference-based generation
