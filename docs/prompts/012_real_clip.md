# Prompt 012: Real CLIP Evaluation

## Summary

이번 prompt는 mock `EvaluationAgent`를 실제 CLIP 기반 image-text similarity evaluation 구조로 확장하기 위한 Sprint 12 Architecture Prompt입니다.

## Purpose

generated image와 final prompt를 CLIP embedding space에서 비교해 0.0~1.0 score를 계산합니다.

## Key Constraints

- `EvaluationAgent.run(reference_image, generated_image_path, final_prompt) -> float` interface 유지
- 실제 CLIP model loading과 inference는 `ClipTool`에서 처리
- model은 lazy loading
- 실패 시 fallback score `0.0` 반환
- UI, Orchestrator, Pipeline, Memory는 수정하지 않음

## Done Definition

- `python -m compileall agents tools workflow memory ui` 성공
- generated image와 final prompt 기반 CLIP score 계산 가능
- CLIP 실패 시 fallback score `0.0` 반환
- 기존 UI와 Orchestrator 수정 없음
- Documentation 업데이트 완료
- Workspace 밖 파일 생성 없음
