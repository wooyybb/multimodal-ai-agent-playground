# Prompt 017: Context Engineering

## Summary

이번 prompt는 PromptAgent를 context-aware prompt builder로 확장하기 위한 Sprint 17 Architecture Prompt입니다.

## Purpose

PromptAgent가 caption과 user prompt뿐 아니라 Orchestrator가 구성한 context dict를 참고해 final prompt를 생성하게 합니다.

## Key Constraints

- PromptAgent는 MemoryManager를 직접 호출하지 않습니다.
- PromptAgent는 PlannerAgent를 직접 호출하지 않습니다.
- OrchestratorAgent가 context를 구성합니다.
- `context`는 optional argument로 두어 backward compatibility를 유지합니다.
- sensitive/path/token 정보는 prompt에 넣지 않습니다.

## Done Definition

- `python -m compileall agents tools workflow memory ui registry` 성공
- 기존 E2E workflow 유지
- PromptAgent가 context 인자를 받을 수 있음
- last_run이 없어도 동작
- last_run이 있으면 previous best prompt 또는 score를 제한적으로 반영 가능
- agent_trace에 context 구성 기록 포함
- Documentation 업데이트 완료
- Workspace 밖 파일 생성 없음
