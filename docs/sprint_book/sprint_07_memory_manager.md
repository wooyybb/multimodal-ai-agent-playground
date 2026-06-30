# Sprint 07

## Objective

실행 결과를 JSON 기반 MemoryManager에 저장합니다.

## Background

Self-improving agent는 이전 prompt, score, reflection, retry 결과를 기억해야 합니다.

## Problem

기존 workflow는 이전 실행을 기억하지 못했습니다.

## Design Decision

`MemoryManager`를 도입하고 `history.json`에 episodic memory를 저장했습니다.

## Architecture

```text
OrchestratorAgent -> MemoryManager(load/save) -> history.json
```

## Implementation Summary

`load_last_run`, `save_run`, `get_history`, `clear_history` interface를 만들었습니다.

## AI Agent Concept

Working Memory and Episodic Memory.

## Prompt Engineering Note

JSON-first MVP와 memory interface를 명확히 요구했습니다.

## Codex Usage

Codex는 memory schema와 문서화를 함께 정리했습니다.

## Debugging Experience

history file이 깨질 수 있으므로 defensive read가 필요함을 배웠습니다.

## Interview Talking Points

- 예상 질문: Memory와 Database의 차이는?
- 예상 답변: Memory는 agent context 개념이고 database는 구현 수단입니다.
- 꼬리 질문: JSON의 한계는?

## Lessons Learned

Memory는 agent가 아니라 state manager로 시작하는 것이 적합했습니다.

## Future Work

JSONL, SQLite, vector memory로 확장합니다.
