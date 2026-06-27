# Prompt 013: Integration & Validation

## Summary

이번 prompt는 기능 추가보다 End-to-End validation과 demo readiness를 목표로 한 Sprint 13 prompt입니다.

## Purpose

Gradio UI에서 image와 user prompt를 입력했을 때 전체 multi-agent workflow가 실행되고, 결과와 agent trace, memory record가 확인되는지 검증합니다.

## Key Constraints

- tools, requirements, README는 수정하지 않습니다.
- 새 Agent를 추가하지 않습니다.
- UI output이 `None` 값으로 깨지지 않도록 처리합니다.
- memory 저장 실패가 workflow를 중단하지 않도록 방어합니다.
- testing, known issues, demo script를 문서화합니다.

## Done Definition

- `python -m compileall agents tools workflow memory ui` 성공
- `python main.py` 실행 가능
- UI에서 None 값으로 깨지지 않음
- agent_trace가 보기 좋게 출력됨
- `docs/testing.md` 생성
- `docs/known_issues.md` 생성
- `docs/demo_script.md` 생성
- `assets/test_images/.gitkeep` 생성
- Documentation 업데이트 완료
- Workspace 밖 파일 생성 없음
