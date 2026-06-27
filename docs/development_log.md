# Development Log

## 2026-06-27

### Initial Project Structure

- 기본 Python 프로젝트 구조를 생성했습니다.
- `agents`, `tools`, `workflow`, `memory`, `ui`, `outputs` 폴더를 구성했습니다.
- 각 Python 패키지에는 `__init__.py`를 추가했습니다.
- 초기 파일은 TODO 수준의 skeleton으로 시작했습니다.

### VisionAgent Mock BLIP Tool

- `VisionAgent`를 구현했습니다.
- `VisionAgent`는 `BlipTool`을 호출하도록 구성했습니다.
- 실제 BLIP 모델은 아직 연결하지 않았고, `BlipTool`은 mock caption을 반환합니다.
- 현재 mock caption은 `"A girl standing in a park"`입니다.

### PromptAgent

- `PromptAgent`를 구현했습니다.
- `caption`과 `user_prompt`를 조합해 `final_prompt`를 생성합니다.
- 빈 `user_prompt`가 들어오면 caption 기반 prompt만 생성하도록 처리했습니다.

### OrchestratorAgent And ReflectionAgent

- `OrchestratorAgent`를 추가했습니다.
- 기존 `MultimodalPipeline`이 직접 agent를 호출하던 구조에서, `OrchestratorAgent`가 `VisionAgent`와 `PromptAgent`를 조율하는 구조로 변경했습니다.
- `ReflectionAgent`를 mock 형태로 추가했습니다.
- 현재는 실제 model integration 없이 Python class 기반 multi-agent 구조를 만드는 단계입니다.
