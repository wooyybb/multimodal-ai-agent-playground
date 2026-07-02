# Prompt Archive 025: Scene Planning

## Purpose

사용자 자연어 요청을 바로 prompt로 만들지 않고, 먼저 scene representation으로 변환하기 위한 architecture prompt다.

## Summary

`ScenePlanningAgent`를 추가하고 `scene_plan`을 LayoutAgent, PoseAgent, ExpressionAgent, PromptAssembler가 선택적으로 반영하도록 설계했다.

## Prompt Engineering Note

중간 표현(Structured Intermediate Representation)을 두면 prompt assembly 전에 scene intent를 명확히 할 수 있다.
