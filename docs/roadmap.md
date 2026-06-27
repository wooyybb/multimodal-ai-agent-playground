# Roadmap

## Sprint 0: Project Skeleton - Done

- 기본 폴더 구조 생성
- Python package 초기화
- TODO skeleton 파일 생성

## Sprint 1: VisionAgent - Done

- `VisionAgent` 구현
- `BlipTool` mock caption 연결
- 이미지 입력에서 caption 반환 흐름 구성

## Sprint 2: PromptAgent - Done

- `PromptAgent` 구현
- caption과 user prompt 조합
- final prompt 생성

## Sprint 3: OrchestratorAgent - Done

- `OrchestratorAgent` 추가
- `VisionAgent`와 `PromptAgent` 조율
- `agent_trace` 반환

## Sprint 4: GenerationAgent Mock - Done

- `GenerationAgent` mock 구현
- final prompt를 받아 PIL mock image 생성
- `outputs/output_mock.png` 저장 경로 반환

## Sprint 5: EvaluationAgent Mock - Done

- `EvaluationAgent` mock 구현
- 생성 결과와 prompt를 받아 mock score 반환

## Sprint 6: Reflection + Retry Loop - Done

- `ReflectionAgent` 개선 제안 로직 확장
- `RetryAgent`를 통해 낮은 score일 때 prompt 개선 및 재시도 흐름 구성

## Sprint 7: Memory

- `MemoryManager` 구현 - Done
- `load_last_run()`, `save_run()`, `get_history()`, `clear_history()` 구현 - Done
- caption, prompt, score, reflection, retry, output image path 저장 - Done
- 향후 prompt 개선에 활용할 memory layer 설계

## Sprint 8: Real BLIP/FLUX/CLIP Integration

- `BlipTool`에 실제 BLIP 연결
- `FluxTool`에 실제 FLUX 또는 image generation API 연결
- `ClipTool`에 실제 CLIP 기반 evaluation 연결

## Sprint 8: One-Step Retry Loop - Done

- initial generation/evaluation 이후 reflection 실행
- retry가 필요한 경우 suggested prompt로 second attempt 실행
- initial/retry 중 best score 선택
- full retry record를 memory에 저장

## Sprint 9: Gradio UI Integration - Done

- Gradio Blocks 기반 UI 구현
- image input과 user prompt 입력 연결
- multi-agent workflow 결과 표시
- agent trace 시각화

## Sprint 10: Real BLIP Integration - Done

- `BlipTool`에 `Salesforce/blip-image-captioning-base` 연결
- lazy loading 기반 BLIP model/processor 로딩
- fallback caption 처리
- `VisionAgent` interface 유지

## Sprint 11: Real FLUX Integration - Done

- `FluxTool`에 Hugging Face `InferenceClient` 기반 FLUX generation 구조 추가
- `HF_TOKEN` 환경변수 기반 API 호출
- API 실패 또는 token 부재 시 fallback mock image 생성
- timestamp 기반 output file 저장

## Sprint 12: Real CLIP Evaluation - Done

- `ClipTool`에 `openai/clip-vit-base-patch32` 기반 evaluation 구조 추가
- generated image와 final prompt의 image-text similarity 계산
- cosine similarity를 0.0~1.0 score로 변환
- CLIP 실패 시 fallback score `0.0` 반환
