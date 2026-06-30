# Demo Script

## 1분 설명용 스크립트

이 프로젝트는 이미지 입력을 받아 BLIP로 caption을 만들고, PromptAgent가 user prompt와 결합한 뒤, FLUX로 이미지를 생성하고 CLIP으로 평가하는 multi-agent workflow입니다. 평가 점수가 낮으면 ReflectionAgent가 개선 방향을 제안하고 RetryAgent가 재시도 여부를 판단합니다. 마지막으로 MemoryManager가 실행 기록을 `history.json`에 저장합니다. 저는 Codex를 단순 코드 생성기가 아니라 sprint 단위 pair engineer처럼 활용해서 agent 구조, tool 분리, fallback 설계, 문서화와 검증까지 단계적으로 진행했습니다.

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

## Demo 실행 흐름

1. `python main.py`로 Gradio UI를 실행합니다.
2. 이미지를 업로드합니다.
3. user prompt를 입력합니다.
4. `Run Multi-Agent Workflow` 버튼을 누릅니다.
5. caption, final prompt, generated image, CLIP score를 확인합니다.
6. reflection, retry decision, best result를 확인합니다.
7. agent trace로 실행 순서를 설명합니다.
8. `memory/history.json`에 저장된 기록을 설명합니다.

## 4. 이미지 업로드 후 흐름 설명

사용자가 이미지를 업로드하고 user prompt를 입력하면 UI는 `MultimodalPipeline`만 호출합니다. Pipeline은 `OrchestratorAgent`를 호출하고, Orchestrator가 각 agent 실행 순서를 관리합니다.

## 5. Agent Trace 설명

UI의 agent trace는 어떤 agent가 어떤 순서로 실행됐는지 보여줍니다. 이를 통해 multi-agent workflow가 실제로 단계별로 동작했음을 설명할 수 있습니다.

## 6. Memory 기록 설명

workflow 종료 시 `MemoryManager`가 `memory/history.json`에 caption, initial score, retry 결과, best result를 저장합니다.

## 7. Codex 사용 방식 설명

Codex는 단순 코드 생성기가 아니라 sprint 기반 junior developer처럼 활용했습니다. 각 Sprint에서 architecture, allowed files, forbidden files, done definition을 명확히 주고 구현과 문서화를 함께 진행했습니다.

Codex 활용 방식의 핵심은 다음과 같습니다.

- sprint별 목표를 architecture prompt로 정의
- 수정 가능한 파일과 금지 파일을 명확히 분리
- mock-first로 agent contract를 먼저 안정화
- BLIP, FLUX, CLIP 통합 시 tool-agent separation 유지
- compileall, fallback test, 문서 업데이트로 완료 기준 검증

## 8. 향후 개선 방향

- 실제 모델 실행 환경 안정화
- output metadata 확장
- history viewer UI 추가
- reference image similarity 추가
- README와 demo video 정리
