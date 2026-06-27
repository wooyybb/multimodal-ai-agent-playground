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
