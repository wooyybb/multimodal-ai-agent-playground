# Demo Script

## 1. 프로젝트 한 줄 소개

이 프로젝트는 이미지 입력과 user prompt를 받아 multi-agent workflow로 caption, prompt, image generation, evaluation, reflection, retry decision, memory 저장까지 수행하는 AI Agent Engineering demo입니다.

## 2. 아키텍처 설명

```text
Gradio UI
-> MultimodalPipeline
-> OrchestratorAgent
-> VisionAgent / BLIP
-> PromptAgent
-> GenerationAgent / FLUX or fallback
-> EvaluationAgent / CLIP
-> ReflectionAgent
-> RetryAgent
-> MemoryManager
```

## 3. Demo 실행 명령어

```bash
python main.py
```

## 4. 이미지 업로드 후 흐름 설명

사용자가 이미지를 업로드하고 user prompt를 입력하면 UI는 `MultimodalPipeline`만 호출합니다. Pipeline은 `OrchestratorAgent`를 호출하고, Orchestrator가 각 agent 실행 순서를 관리합니다.

## 5. Agent Trace 설명

UI의 agent trace는 어떤 agent가 어떤 순서로 실행됐는지 보여줍니다. 이를 통해 multi-agent workflow가 실제로 단계별로 동작했음을 설명할 수 있습니다.

## 6. Memory 기록 설명

workflow 종료 시 `MemoryManager`가 `memory/history.json`에 caption, initial score, retry 결과, best result를 저장합니다.

## 7. Codex 사용 방식 설명

Codex는 단순 코드 생성기가 아니라 sprint 기반 junior developer처럼 활용했습니다. 각 Sprint에서 architecture, allowed files, forbidden files, done definition을 명확히 주고 구현과 문서화를 함께 진행했습니다.

## 8. 향후 개선 방향

- 실제 모델 실행 환경 안정화
- output metadata 확장
- history viewer UI 추가
- reference image similarity 추가
- README와 demo video 정리
