# Testing

## End-to-End Test 목적

End-to-End Test의 목적은 Gradio UI에서 이미지와 user prompt를 입력했을 때 전체 multi-agent workflow가 끊기지 않고 실행되는지 확인하는 것입니다.

검증 대상 흐름:

```text
UI -> Pipeline -> OrchestratorAgent -> VisionAgent -> PromptAgent -> GenerationAgent -> EvaluationAgent -> ReflectionAgent -> RetryAgent -> MemoryManager -> UI Output
```

## 테스트 방법

1. `python main.py`로 Gradio UI를 실행합니다.
2. 테스트 이미지를 업로드합니다.
3. user prompt를 입력합니다.
4. `Run Multi-Agent Workflow` 버튼을 클릭합니다.
5. 출력 필드와 agent trace를 확인합니다.
6. `memory/history.json`에 기록이 저장됐는지 확인합니다.

## 테스트 이미지 종류

- cat
- car
- landscape
- person
- illustration

실제 이미지 파일은 repository에 포함하지 않고, `assets/test_images/` 폴더만 유지합니다.

## 확인 항목

- BLIP caption
- final prompt
- output image
- CLIP score
- reflection
- retry decision
- best result
- `memory/history.json` 저장
- agent_trace
