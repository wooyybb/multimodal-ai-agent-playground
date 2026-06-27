# Prompt 007: Memory Manager

## Summary

이번 prompt는 Sprint 7 Memory Engineering을 위한 Architecture Prompt입니다.

## Structure

```text
Task
↓
Architecture
↓
Workspace
↓
Allowed Files
↓
Forbidden Files
↓
Requirements
↓
Documentation
↓
Done Definition
```

## Intent

목표는 단순히 `history.json`을 쓰는 기능이 아니라, AI Agent가 과거 실행을 다룰 수 있는 Memory Interface를 설계하는 것입니다.

## Key Requirements

- `MemoryManager` class 도입
- `load_last_run()`
- `save_run()`
- `get_history()`
- `clear_history()`
- Orchestrator 시작 시 load
- Orchestrator 종료 시 save
- Documentation과 Prompt Engineering 기록 업데이트

## Done Definition

- `python -m compileall agents tools workflow memory ui` 성공
- `history.json` 생성 가능
- Memory 저장 가능
- Memory 조회 가능
- Documentation 업데이트 완료
- Workspace 밖 파일 생성 없음
