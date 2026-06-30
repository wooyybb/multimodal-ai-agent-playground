# Prompt Archive 019: Dynamic Execution Engine

## Purpose

이번 prompt는 Planner-driven Workflow를 구현하기 위한 architecture refactoring prompt다.

## Summary

요구사항은 PlannerAgent가 만든 `execution_plan`을 OrchestratorAgent가 직접 해석하지 않고, `DynamicExecutionEngine`이 state와 ToolRegistry를 이용해 실행하도록 만드는 것이다.

## Prompt Constraints

- Workspace 내부에서만 작업
- 허용 파일과 금지 파일을 명확히 분리
- 기존 agent interface 유지
- 기존 UI 반환 key 유지
- one-step retry policy 유지
- memory save failure가 전체 workflow를 중단하지 않도록 처리

## Prompt Engineering Note

이번 prompt는 architecture refactoring에서 기존 E2E 동작을 보존하기 위해 state schema와 step behavior를 구체적으로 제시했다. 이 덕분에 Codex가 Orchestrator를 과도하게 바꾸지 않고 실행 책임만 분리할 수 있었다.
