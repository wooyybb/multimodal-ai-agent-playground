# Prompts

## Skeleton 생성

프로젝트의 기본 폴더 구조와 Python package skeleton을 생성했습니다. `agents`, `tools`, `workflow`, `memory`, `ui`, `outputs` 폴더를 만들고, 각 Python 폴더에 `__init__.py`와 TODO 수준의 파일을 추가했습니다.

## VisionAgent 구현

`VisionAgent`가 이미지를 입력받아 caption을 반환하는 구조를 구현했습니다. 실제 BLIP는 연결하지 않고 `BlipTool`을 통해 mock caption을 반환하도록 했습니다.

## PromptAgent 구현

`PromptAgent`가 `caption`과 `user_prompt`를 조합해 `final_prompt`를 생성하도록 구현했습니다. 빈 user prompt가 들어올 경우 caption 기반 prompt만 생성하도록 처리했습니다.

## OrchestratorAgent 추가

기존 `workflow/pipeline.py` 중심 구조를 유지하면서 `OrchestratorAgent`를 추가했습니다. `OrchestratorAgent`가 `VisionAgent`와 `PromptAgent`를 호출하고, 결과와 `agent_trace`를 반환하는 multi-agent workflow 형태로 발전시켰습니다.
