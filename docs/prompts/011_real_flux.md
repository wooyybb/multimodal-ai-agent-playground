# Prompt 011: Real FLUX Integration

## Summary

이번 prompt는 mock `GenerationAgent`를 실제 FLUX 기반 image generation 구조로 확장하기 위한 Sprint 11 Architecture Prompt입니다.

## Purpose

`GenerationAgent`가 `FluxTool`을 통해 Hugging Face FLUX generation을 시도하고, 실패 시 fallback mock image를 생성하게 합니다.

## Key Constraints

- `GenerationAgent.run(final_prompt) -> str` interface 유지
- 실제 API 호출과 fallback은 `FluxTool`에서 처리
- `HF_TOKEN`은 환경변수로만 관리
- UI, Orchestrator, Pipeline, Memory는 수정하지 않음
- API 실패 시 workflow가 멈추지 않도록 fallback image 생성

## Done Definition

- `python -m compileall agents tools workflow memory ui` 성공
- `HF_TOKEN`이 있으면 real FLUX generation 시도
- `HF_TOKEN`이 없으면 fallback mock image 생성
- `outputs/`에 image 저장
- 기존 UI와 Orchestrator 수정 없음
- Documentation 업데이트 완료
- Workspace 밖 파일 생성 없음
