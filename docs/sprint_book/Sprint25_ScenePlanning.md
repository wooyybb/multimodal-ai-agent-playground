# Sprint 25: Scene Planning Agent

## Objective

사용자 요청을 scene type, emotion, relationship, interaction, camera intent로 구조화하는 ScenePlanningAgent를 추가한다.

## Problem

기존 구조는 Layout/Pose/Expression을 각각 만들었지만, 전체 장면 의도를 먼저 해석하는 계층이 없었다.

## Design Decision

ScenePlanningAgent를 추가하고 `scene_plan`을 downstream prompt section agents에 전달한다.

## Implementation Summary

- `agents/scene_planning_agent.py` 추가
- Planner execution plan에 `scene_planning` 추가
- Orchestrator registry에 `scene_planning` 등록
- ExecutionEngine에서 `state["scene_plan"]` 저장
- LayoutAgent, PoseAgent, ExpressionAgent, PromptAssembler가 scene_plan 반영

## AI Agent Concept

Scene Plan은 prompt generation 전의 structured intermediate representation이다.

## Prompt Engineering Note

사용자 자연어를 곧바로 generation prompt로 바꾸지 않고 scene plan으로 해석한 뒤 prompt section에 반영한다.

## Interview Talking Points

Q. Scene Plan과 Layout Plan의 차이는?
A. Scene Plan은 무엇이 벌어지는 장면인지, Layout Plan은 그 장면을 어떻게 배치할지 설명합니다.

## Future Work

- LLM scene planner
- scene graph
- character relationship agent
