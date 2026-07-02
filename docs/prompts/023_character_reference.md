# Prompt Archive 023: Character Reference Handling

## Purpose

이번 prompt는 여러 uploaded image를 각각 별도 character reference로 취급하기 위한 schema-first architecture prompt다.

## Summary

`CharacterAgent`는 `character_count`, `characters`, `global_character_rules`를 반환하고, `PromptAssembler`는 character preservation rules를 generation prompt에 압축해 반영한다.

## Constraints

- UI 수정 금지
- Vision/Gene­ration/Evaluation/Retry agent 수정 금지
- 실제 multi-image captioning은 구현하지 않음
- single-image workflow fallback 유지

## Prompt Engineering Note

긴 identity preservation prompt를 구조화된 character schema와 compact generation prompt rule로 분리했다.
