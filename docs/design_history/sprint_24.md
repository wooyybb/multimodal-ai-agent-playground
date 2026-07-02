# Sprint 24: Layout Planning Agent

## Problem

LayoutAgent가 단순 keyword만 만들고 있어 frame, camera, subject placement, cropping 같은 composition 요소를 충분히 계획하지 못했다.

## Decision

LayoutAgent를 Layout Plan generator로 변경하고 PromptAssembler가 이 plan을 generation prompt로 변환하도록 했다.

## Alternatives

- 기존 keyword 방식 유지
- PromptAssembler에서 layout 추론
- LLM 기반 layout planner
- UI에서 layout 선택

## Reason

LayoutAgent가 composition planning을 담당하면 visual structure를 독립적으로 개선할 수 있고, PromptAssembler는 assembly 책임에 집중할 수 있다.

## Future Work

- camera-aware evaluation
- layout templates
- photobooth layout presets
- visual composition scoring
