# Retrospective

## 잘된 점

- Reflection, Retry, Memory의 책임을 분리했습니다.
- 실제 LLM이나 무거운 라이브러리 없이 feedback loop contract를 만들었습니다.
- `history.json` 저장으로 향후 개선 분석의 기반을 마련했습니다.

## 아쉬운 점

- 아직 실제 regeneration loop는 없습니다.
- Reflection은 rule-based mock이라 복잡한 실패 원인을 분석하지는 못합니다.
- Memory는 append-only JSON 저장이라 검색이나 요약 기능은 없습니다.

## 다음 Sprint

- 실제 retry loop 연결
- retry 횟수 제한과 stop condition 설계
- memory history를 활용한 prompt 개선 로직 설계

## Memory Engineering Follow-up

### 잘된 점

- `MemoryManager` interface가 명확해졌습니다.
- `load_last_run()`과 `save_run()`이 orchestrator lifecycle에 연결됐습니다.
- `history.json`이 episodic memory 역할을 하도록 확장됐습니다.

### 아쉬운 점

- 아직 memory를 prompt 생성이나 reflection 개선에 직접 사용하지는 않습니다.
- JSON 파일이 커질 때의 성능 대책은 없습니다.

### 다음 Sprint

- last run context를 `PromptAgent` 또는 `ReflectionAgent`에 활용
- retry loop 실행 시 memory에 attempt 단위 기록 저장
- JSONL 또는 SQLite 전환 검토

## Sprint 8 Retrospective

### 잘된 점

- one-step retry loop로 self-improving behavior가 코드에 반영됐습니다.
- retry policy와 workflow control 책임이 분리됐습니다.
- initial, retry, best 결과를 memory에 저장할 수 있게 됐습니다.

### 아쉬운 점

- mock generation이 같은 output path를 사용해 attempt별 이미지 구분은 아직 약합니다.
- retry prompt가 실제 이미지 품질을 개선하는지는 mock score 환경이라 제한적으로만 확인됩니다.

### 다음 Sprint

- attempt별 output filename 분리
- retry count와 stop condition을 설정 가능한 policy로 확장
- memory history를 reflection context로 활용

## Sprint 9 Retrospective

### 잘된 점

- UI와 workflow 책임을 분리했습니다.
- Gradio Blocks로 image input, prompt input, workflow result를 빠르게 연결했습니다.
- Agent trace를 UI에 노출해 multi-agent 실행 흐름을 설명할 수 있게 됐습니다.

### 아쉬운 점

- 아직 mock image와 mock score 기반 demo입니다.
- UI styling은 최소 수준입니다.
- `python main.py`는 Gradio server를 실행하므로 자동 테스트에서는 app 생성까지만 확인하는 편이 안전합니다.

### 다음 Sprint

- output image 파일명을 attempt별로 분리
- UI에서 history 보기 기능 추가
- 실제 BLIP/FLUX/CLIP 연동 전 demo 시나리오 정리
