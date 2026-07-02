# Sprint 25: Scene Planning Agent

## Problem

Layout, Pose, Expression은 각각 생성되고 있었지만 사용자 요청이 말하는 전체 상황(scene)을 먼저 구조화하지 못했다.

## Decision

`ScenePlanningAgent`를 추가해 `scene_type`, `emotion`, `relationship`, `interaction`, `energy`, `camera_intent`, `narrative`를 구조화한다.

## Alternatives

- LayoutAgent가 scene parsing까지 담당
- PromptAssembler에서 직접 scene 해석
- LLM Planner로 바로 전환
- 기존 PromptAgent 기반 유지

## Reason

Scene Plan은 Layout/Pose/Expression보다 상위 개념이다. 별도 agent로 분리하면 downstream agents가 같은 scene interpretation을 공유할 수 있다.

## Future Work

- LLM-based scene planner
- scene graph generation
- character relationship modeling
- multi-panel narrative planning
