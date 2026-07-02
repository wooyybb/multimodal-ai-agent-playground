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

## Sprint 10 Retrospective

### 잘된 점

- mock VisionAgent에서 실제 BLIP captioning tool로 전환했습니다.
- Tool-Agent Separation을 유지했습니다.
- lazy loading과 fallback caption으로 model integration 위험을 줄였습니다.

### 아쉬운 점

- BLIP 모델 다운로드가 필요한 환경에서는 첫 실행 시간이 길 수 있습니다.
- 오프라인 환경에서는 실제 caption 대신 fallback caption이 반환됩니다.

### 다음 Sprint

- BLIP inference 결과를 UI에서 실제 이미지로 검증
- model cache와 device 설정 문서화
- 실제 FLUX 또는 CLIP 통합으로 확장

## Sprint 11 Retrospective

### 잘된 점

- mock generation에서 real FLUX API generation 구조로 확장했습니다.
- `GenerationAgent` interface를 유지했습니다.
- API 실패에도 fallback image로 workflow가 계속됩니다.

### 아쉬운 점

- 실제 FLUX API 성공 여부는 `HF_TOKEN`과 network 상태에 의존합니다.
- fallback image는 실제 generation 품질을 반영하지 않습니다.

### 다음 Sprint

- 실제 API 호출 성공 케이스 검증
- output metadata 저장
- seed, width, height 같은 generation option 추가

## Sprint 12 Retrospective

### 잘된 점

- mock evaluation에서 CLIP 기반 model-based evaluation 구조로 확장했습니다.
- `EvaluationAgent` interface를 유지했습니다.
- lazy loading과 fallback score로 실패 안전성을 확보했습니다.

### 아쉬운 점

- 실제 CLIP model 다운로드가 필요한 환경에서는 첫 평가 시간이 길 수 있습니다.
- CLIP score는 prompt alignment 중심이라 이미지 품질 전체를 평가하지는 못합니다.

### 다음 Sprint

- reference image similarity 추가
- DINO similarity 또는 aesthetic score 보강
- UI에 evaluation explanation 추가

## Sprint 13 Retrospective

### 잘된 점

- E2E validation 관점에서 전체 workflow를 정리했습니다.
- UI 안정성과 memory save 방어 처리를 보강했습니다.
- demo script와 known issues를 문서화했습니다.

### 아쉬운 점

- 아직 자동화된 integration test는 없습니다.
- 실제 모델 다운로드와 API 호출 성공 여부는 환경에 따라 달라집니다.

### 다음 Sprint

- 자동화된 smoke test 추가
- history viewer UI 추가
- README와 demo video 정리

## Sprint 15 Retrospective

### 잘된 점

- PlannerAgent를 추가해 fixed workflow에서 agentic planning 구조로 확장할 기반을 만들었습니다.
- Planner와 Orchestrator의 책임을 분리했습니다.
- 기존 E2E workflow를 깨지 않고 planner_result를 기록했습니다.

### 아쉬운 점

- execution_plan은 아직 실제 dynamic execution engine에 사용되지 않습니다.
- Planner는 rule-based라 복잡한 사용자 의도를 해석하지는 못합니다.

### 다음 Sprint

- execution_plan 기반 conditional execution 검토
- LLM-based planning 실험
- plan과 실제 agent_trace를 비교하는 validation 추가

## Sprint 16 Retrospective

### 잘된 점

- ToolRegistry를 도입해 Orchestrator와 Agent 호출 사이의 결합도를 낮췄습니다.
- Planner execution plan 이름과 registry tool 이름을 맞춰 future dynamic engine 기반을 만들었습니다.
- 기존 E2E workflow를 유지했습니다.

### 아쉬운 점

- 아직 execution_plan을 loop로 실행하지는 않습니다.
- 각 tool의 argument schema는 명시적으로 관리하지 않습니다.

### 다음 Sprint

- Context Engineering
- execution_plan 기반 dynamic execution
- tool argument schema와 validation 추가

## Sprint 17 Retrospective

### 잘된 점

- PromptAgent를 context-aware prompt builder로 확장했습니다.
- Orchestrator 중심 context composition으로 책임 분리를 유지했습니다.
- 기존 호출과 E2E workflow를 깨지 않았습니다.

### 아쉬운 점

- context dict schema validation은 아직 없습니다.
- previous best prompt 활용은 간단한 문자열 요약 수준입니다.

### 다음 Sprint

- RAG Style Library
- Semantic Memory 검색
- Prompt template selection
## Sprint 18 Retrospective

### 잘된 점

- PromptAgent의 책임을 prompt composition으로 좁히고 compression 책임을 분리했습니다.
- CLIP token limit 문제를 architecture 수준에서 다뤘습니다.

### 아쉬운 점

- 아직 실제 tokenizer 기반 token counting은 구현하지 않았습니다.

### 다음 Sprint

- RAG Style Library 또는 Semantic Memory를 통해 압축 context의 품질을 높입니다.
## Sprint 19 Retrospective

### 잘된 점

- Planner-driven workflow의 첫 구조를 만들었습니다.
- OrchestratorAgent의 책임이 줄고 실행 로직이 분리되었습니다.
- 기존 one-step retry와 memory save 흐름을 유지했습니다.

### 아쉬운 점

- 아직 conditional branch나 parallel execution은 구현하지 않았습니다.
- state dict는 빠르게 구현하기 좋지만 type safety는 부족합니다.

### 다음 Sprint

- RAG Style Library 또는 Semantic Memory를 연결해 dynamic workflow의 분기 가능성을 높입니다.
## Sprint 20 Retrospective

### 잘된 점

- Vector DB 없이도 RAG의 핵심 구조를 구현했습니다.
- KnowledgeManager와 RetrievalAgent의 책임을 분리했습니다.
- DynamicExecutionEngine에 retrieval step을 자연스럽게 추가했습니다.

### 아쉬운 점

- 현재 retrieval은 keyword matching 기반이라 semantic search는 아직 지원하지 않습니다.

### 다음 Sprint

- Semantic Memory 또는 Vector DB adapter를 검토합니다.
## Sprint 21 Retrospective

### 잘된 점

- Memory retrieval interface를 만들었습니다.
- PlannerAgent를 수정하지 않고 ExecutionEngine에서 step을 자동 삽입했습니다.
- full history를 prompt에 넣지 않고 짧은 hint만 사용했습니다.

### 아쉬운 점

- keyword similarity는 의미적 유사도를 충분히 반영하지 못합니다.

### 다음 Sprint

- ChromaDB 또는 embedding 기반 semantic memory로 확장합니다.
## Sprint 22 Retrospective

### 잘된 점

- Prompt engineering 책임을 role-based agent로 분리했습니다.
- 기존 generation/evaluation/retry workflow를 유지했습니다.
- PromptAssembler로 final prompt assembly 책임을 명확히 했습니다.

### 아쉬운 점

- 각 role agent는 아직 rule-based skeleton입니다.

### 다음 Sprint

- PromptRouter 또는 typed prompt fragment schema를 도입합니다.
## Sprint22 Detailed Retrospective

### 잘된 점

- Prompt section responsibility became clearer.
- Negative prompt is now separated in state.
- Existing BLIP/FLUX/CLIP workflow remains intact.

### 다음 Sprint

- Character reference handling
- Negative prompt routing
- Provider-specific prompt adapters
## Sprint23 Retrospective

### 잘된 점

- Character schema now supports future multi-image input.
- Identity preservation rules are centralized in PromptAssembler.
- Existing single-image workflow remains intact.

### 다음 Sprint

- Multi-image UI or Photobooth Layout Agent.
## Sprint24 Retrospective

### 잘된 점

- LayoutAgent responsibility became clearer.
- Camera view and subject placement are now explicit.
- PromptAssembler uses structured layout data.

### 다음 Sprint

- Photobooth-specific layout templates or composition evaluation.
## Sprint25 Retrospective

### 잘된 점

- Scene-level intent is now explicit.
- Downstream agents can share the same scene interpretation.
- Existing workflow remains intact.

### 다음 Sprint

- Character relationship modeling or provider-specific prompt adapters.
