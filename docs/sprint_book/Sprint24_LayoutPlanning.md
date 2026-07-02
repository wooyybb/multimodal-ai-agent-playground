# Sprint 24: Layout Planning Agent

## Objective

LayoutAgent를 단순 keyword generator에서 visual composition을 계획하는 Layout Planning Agent로 발전시킨다.

## Problem

기존 LayoutAgent는 photobooth, vertical 같은 keyword만 반환했다. 하지만 이미지 생성에서는 frame structure, camera view, subject placement, background, composition hierarchy가 중요하다.

## Design Decision

LayoutAgent가 `layout_type`, `aspect_ratio`, `frame_structure`, `camera_view`, `subject_placement`, `background_style`, `composition_rules`를 포함한 Layout Plan을 반환하도록 변경했다.

## Implementation Summary

- LayoutAgent가 supported layout types를 감지
- camera view와 subject placement planning 추가
- layout type별 composition rules 추가
- PromptAssembler가 Layout Plan을 generation prompt phrase로 변환

## AI Agent Concept

Layout Planning은 prompt keyword 생성이 아니라 시각적 구조를 먼저 계획하는 agent behavior다.

## Prompt Engineering Note

layout keyword를 그대로 붙이지 않고, frame/camera/placement/background/rule을 generation prompt로 변환한다.

## Interview Talking Points

Q. LayoutAgent는 Prompt를 만드는 Agent인가요?
A. 직접 final prompt를 만들기보다 visual layout plan을 만들고 PromptAssembler가 이를 prompt로 변환합니다.

Q. Composition Planning이 중요한 이유는?
A. 생성 모델은 subject placement, camera view, frame structure에 크게 영향을 받기 때문입니다.

## Future Work

- Photobooth-specific layout planner
- multi-image UI layout mapping
- composition score evaluator
