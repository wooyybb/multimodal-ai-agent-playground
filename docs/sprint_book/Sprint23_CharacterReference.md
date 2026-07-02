# Sprint 23: Character Reference Handling

## Objective

여러 reference image를 각각 별도 character로 취급하고, identity preservation rule을 generation prompt에 반영한다.

## Problem

single image caption 중심 구조에서는 여러 캐릭터가 섞이거나 outfit, hairstyle, silhouette이 바뀌는 문제를 prompt 단계에서 충분히 방어하기 어렵다.

## Design Decision

CharacterAgent가 multi-character schema를 만들고 PromptAssembler가 compact character preservation rule을 generation prompt에 추가한다.

## Implementation Summary

- `CharacterAgent`가 항상 `character_count`, `characters`, `global_character_rules` schema 반환
- `reference_images`, `character_inputs`, list image fallback 지원
- user prompt의 `two characters`, `friends`, `couple`, `photobooth` 힌트로 character count 추정
- `PromptAssembler`가 preservation rules를 generation prompt에 반영
- single-image workflow 유지

## AI Agent Concept

Character Reference Handling은 uploaded reference를 단순 image input이 아니라 identity-preserving character source로 해석하는 prompt architecture다.

## Prompt Engineering Note

긴 preservation 문장을 반복하지 않고 “separate recognizable characters, preserve outfit/hairstyle/silhouette/proportions/vibe/color balance, do not merge” 형태로 압축했다.

## Interview Talking Points

Q. Character Reference Handling이란 무엇인가요?
A. reference image를 character identity source로 보고 생성 prompt에 identity preservation rule을 반영하는 구조입니다.

Q. 여러 reference image가 있을 때 캐릭터가 섞이는 문제를 어떻게 방지하나요?
A. 각 uploaded image를 one separate character로 보고 do not merge rule을 prompt에 명시합니다.

## Future Work

- multi-image UI
- per-character captioning
- identity similarity evaluation
- provider-specific reference control
