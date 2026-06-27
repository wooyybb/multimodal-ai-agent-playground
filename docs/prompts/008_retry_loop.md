# Prompt 008: One-Step Retry Loop

## Summary

이번 prompt는 Evaluation, Reflection, Retry, Regeneration 흐름을 구현하기 위한 Sprint 8 Architecture Prompt입니다.

## Purpose

목표는 score가 threshold보다 낮을 때 `ReflectionAgent`의 `suggested_prompt`를 사용해 한 번 더 generation과 evaluation을 수행하는 것입니다.

## Key Constraints

- Retry는 최대 1회만 수행합니다.
- `RetryAgent`는 retry 여부만 판단합니다.
- `OrchestratorAgent`가 loop를 제어합니다.
- initial attempt, retry attempt, best result를 모두 memory에 저장합니다.
- README, main, requirements는 수정하지 않습니다.

## Done Definition

- `python -m compileall agents tools workflow memory ui` 성공
- retry_needed=True일 때 second attempt 실행 가능
- retry_needed=False일 때 retry skip 가능
- best_score 선택 가능
- `history.json`에 initial/retry/best 정보 저장 가능
- Documentation 업데이트 완료
- Workspace 밖 파일 생성 없음
