# Prompt 009: Gradio UI Integration

## Summary

이번 prompt는 multi-agent workflow를 Gradio UI에 연결하기 위한 Sprint 9 Architecture Prompt입니다.

## Purpose

사용자가 이미지를 업로드하고 user prompt를 입력하면 `MultimodalPipeline`을 통해 전체 agent workflow를 실행하고 결과를 UI에서 확인할 수 있게 합니다.

## Key Constraints

- UI는 agent를 직접 호출하지 않습니다.
- UI는 `MultimodalPipeline`만 호출합니다.
- Agent, tools, memory, requirements는 수정하지 않습니다.
- output image path가 `None`이면 UI image output도 `None`으로 처리합니다.
- workflow 예외는 UI error message로 표시합니다.

## Done Definition

- `python -m compileall agents tools workflow memory ui` 성공
- `python main.py` 실행 가능
- Gradio UI 실행 가능
- 이미지 업로드 가능
- user prompt 입력 가능
- Agent workflow 결과 표시 가능
- agent_trace 표시 가능
- Documentation 업데이트 완료
- Workspace 밖 파일 생성 없음
