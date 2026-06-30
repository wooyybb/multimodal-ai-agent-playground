# Sprint Book

## Project Vision

이 프로젝트는 이미지 입력을 받아 BLIP captioning, prompt generation, FLUX image generation, CLIP evaluation, reflection, retry, memory까지 연결하는 Multi-Agent AI Engineering 프로젝트입니다.

목표는 단순 기능 구현이 아니라 Agent 역할 분리, Tool-Agent Separation, Evaluation Loop, Memory, Planning을 sprint 단위로 학습하고 설명 가능한 포트폴리오로 만드는 것입니다.

## Phase

- Phase 1: Project skeleton and basic agents
- Phase 2: Multi-agent orchestration
- Phase 3: Reflection, retry, memory
- Phase 4: Real model integration
- Phase 5: UI, validation, demo readiness
- Phase 6: Planning and future dynamic execution

## Sprint Index

- [Sprint 00 - Project Setup](sprint_00_project_setup.md)
- [Sprint 01 - VisionAgent](sprint_01_vision_agent.md)
- [Sprint 02 - PromptAgent](sprint_02_prompt_agent.md)
- [Sprint 03 - OrchestratorAgent](sprint_03_orchestrator_agent.md)
- [Sprint 04 - GenerationAgent](sprint_04_generation_agent.md)
- [Sprint 05 - EvaluationAgent](sprint_05_evaluation_agent.md)
- [Sprint 06 - Reflection + Retry](sprint_06_reflection_retry.md)
- [Sprint 07 - MemoryManager](sprint_07_memory_manager.md)
- [Sprint 08 - Retry Loop](sprint_08_retry_loop.md)
- [Sprint 09 - Gradio UI](sprint_09_gradio_ui.md)
- [Sprint 10 - Real BLIP](sprint_10_real_blip.md)
- [Sprint 11 - Real FLUX](sprint_11_real_flux.md)
- [Sprint 12 - Real CLIP](sprint_12_real_clip.md)
- [Sprint 13 - Integration Test](sprint_13_integration_test.md)
- [Sprint 14 - PlannerAgent Planned](sprint_14_planner_agent_planned.md)

## Architecture Evolution

```text
Single Pipeline
-> Multi-Agent Orchestration
-> Reflection and Retry
-> MemoryManager
-> Real BLIP / FLUX / CLIP tools
-> Gradio UI
-> Validation and Planner layer
```

## Learning Journey

각 Sprint는 "무엇을 만들었는가"보다 "왜 그렇게 설계했는가"를 기록합니다. Agent 책임 분리, fallback strategy, lazy loading, memory interface, planning boundary를 설명 가능한 형태로 남깁니다.

## Interview Usage

면접에서는 Sprint Book을 다음 흐름으로 활용합니다.

1. 프로젝트 목표를 30초로 설명합니다.
2. architecture evolution을 보여줍니다.
3. 관심 있는 Sprint를 골라 design decision을 설명합니다.
4. known issues와 future work를 정직하게 설명합니다.
5. Codex를 어떻게 engineering partner로 활용했는지 말합니다.
