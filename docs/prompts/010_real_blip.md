# Prompt 010: Real BLIP Integration

## Summary

이번 prompt는 mock `VisionAgent`를 실제 BLIP 기반 image captioning module로 교체하기 위한 Sprint 10 Architecture Prompt입니다.

## Purpose

사용자가 업로드한 이미지를 실제 BLIP model로 captioning해 downstream prompt generation에 전달합니다.

## Key Constraints

- `VisionAgent` interface는 유지합니다.
- 실제 model loading과 inference는 `BlipTool`만 담당합니다.
- model은 lazy loading합니다.
- BLIP 실패 시 fallback caption을 반환합니다.
- UI, orchestrator, pipeline, memory는 수정하지 않습니다.

## Done Definition

- `python -m compileall agents tools workflow memory ui` 성공
- 이미지 업로드 시 mock caption이 아닌 BLIP caption 생성 가능
- BLIP 실패 시 fallback caption 반환
- 기존 UI와 Orchestrator 수정 없음
- Documentation 업데이트 완료
- Workspace 밖 파일 생성 없음
