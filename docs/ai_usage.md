# AI Usage

## Sprint 7

이번 Sprint에서 Codex는 Reflection 기반 Self-Improving AI Agent 구조를 구현하고 문서화하는 데 사용했습니다.

활용 방식:

- 허용 파일과 금지 파일 제약을 지키며 코드 수정
- `ReflectionAgent`, `RetryAgent`, `Memory` 구현
- `OrchestratorAgent` 호출 순서 정리
- sprint 문서 작성 및 architecture 설명 보강
- `compileall`과 pipeline 실행으로 동작 검증

Codex는 구현 assistant로 사용했고, architecture 방향과 sprint 목표는 prompt에서 명확히 지정했습니다.

## Sprint 7 Memory Engineering

이번 Sprint에서 Codex는 `MemoryManager` interface 구현과 관련 문서 업데이트에 활용했습니다.

활용 방식:

- 기존 `History` 구조를 분석하고 `MemoryManager`로 확장
- Orchestrator lifecycle에 `load_last_run()`과 `save_run()` 연결
- `history.json` schema에 `output_image_path` 추가
- architecture, concepts, interview notes, design history 문서 업데이트
- compileall, pipeline 실행, memory 조회로 Done Definition 검증

## Sprint 8 One-Step Retry Loop

이번 Sprint에서 Codex는 retry loop 구현 범위를 제한하고 검증하는 데 활용했습니다.

- 무한 loop 방지를 위해 one-step retry만 구현
- 수정 가능한 파일 범위를 제한해 unrelated churn 방지
- `RetryAgent`는 판단만 하고 `OrchestratorAgent`가 loop를 제어하도록 책임 분리
- initial, retry, best 결과를 memory에 저장하도록 record schema 확장
- Done Definition에 맞춰 compileall, retry true/false 흐름, memory 저장을 확인

## Sprint 9 Gradio UI Integration

이번 Sprint에서 Codex는 UI 수정 가능 파일과 agent 수정 금지 파일을 분리해 Gradio UI를 연결하는 데 활용했습니다.

- `ui/app.py`, `main.py`, `workflow/pipeline.py`만 코드 수정
- Agent 구현 파일, tools, memory, requirements는 수정하지 않음
- UI가 `MultimodalPipeline`만 호출하도록 책임 경계 유지
- Error handling과 agent trace display를 UI에 반영
- compileall과 Gradio app 생성으로 실행 가능성 검증
