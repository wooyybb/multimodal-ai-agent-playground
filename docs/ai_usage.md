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

## Sprint 10 Real BLIP Integration

이번 Sprint에서 Codex는 실제 모델 통합 작업을 하되 기존 interface를 유지하는 방향으로 활용했습니다.

- `VisionAgent.run(image) -> str` interface 유지
- 실제 BLIP integration은 `BlipTool`에만 격리
- lazy loading과 fallback caption을 명시해 failure-safe 구조 구현
- 수정 가능 파일과 금지 파일을 분리해 UI, orchestrator, memory 변경을 방지
- compileall과 fallback path 테스트로 기본 안정성 확인

## Sprint 11 Real FLUX Integration

이번 Sprint에서 Codex는 외부 API 연동 작업을 하되 보안 정보와 수정 범위를 제한하는 방식으로 활용했습니다.

- `HF_TOKEN`을 환경변수로만 사용하도록 구현
- `.env.example`에는 placeholder만 기록
- `FluxTool`에 API 호출과 fallback generation을 격리
- `GenerationAgent` interface 유지
- compileall과 fallback generation 테스트로 workflow 안정성 확인

## Sprint 12 Real CLIP Evaluation

이번 Sprint에서 Codex는 실제 CLIP evaluation 통합 작업에 활용했습니다.

- `EvaluationAgent` interface 유지
- CLIP model loading과 inference를 `ClipTool`에 격리
- lazy loading과 fallback score로 failure-safe 구조 구현
- 수정 범위를 `ClipTool`, `EvaluationAgent`, docs로 제한
- compileall과 fallback score 테스트로 기본 안정성 확인

## Sprint 13 Integration & Validation

이번 Sprint에서 Codex는 기능 구현보다 테스트 문서화와 안정성 개선에 활용했습니다.

- UI output defensive formatting 점검
- agent trace 표시 안정화
- memory save failure handling 보강
- testing, known issues, demo script 문서 작성
- Done Definition 기반 compileall과 UI helper 검증 수행

## Sprint 15 PlannerAgent

이번 Sprint에서 Codex는 architecture-changing task를 단계적으로 적용하는 데 활용했습니다.

- `PlannerAgent` 추가
- Orchestrator 시작 단계에 planning 호출 연결
- dynamic execution engine은 제외하고 기존 workflow 유지
- files forbidden을 통해 tools, UI, requirements 변경 방지
- compileall과 planner_result 확인으로 Done Definition 검증

## Sprint 16 Tool Registry

이번 Sprint에서 Codex는 구조 변경 작업을 하되 기존 E2E 동작 보존을 Done Definition으로 두고 활용했습니다.

- `ToolRegistry` 추가
- Orchestrator 내부 호출을 registry 기반 호출로 감싸기
- tools, UI, memory, requirements 변경 금지
- Planner execution_plan 이름과 registry tool 이름 정렬
- compileall과 pipeline 실행으로 registry 호출 trace 확인

## Sprint 17 Context Engineering

이번 Sprint에서 Codex는 backward compatibility와 context 제한을 명시한 상태에서 PromptAgent를 확장하는 데 활용했습니다.

- `context`를 optional argument로 추가
- Orchestrator가 context dict를 구성하도록 책임 분리
- sensitive/path/token 정보가 prompt에 들어가지 않도록 제한
- compileall과 PromptAgent 단독 테스트로 기존 호출과 context 호출 모두 검증
## Sprint 18 AI Usage

Codex는 Sprint18 prompt를 기반으로 허용된 파일 범위 안에서 PromptCompressor 설계, PromptAgent 수정, Orchestrator 연결, 문서 업데이트를 수행했습니다. 특히 raw context를 직접 prompt에 넣지 않는 규칙을 코드와 문서에 함께 반영했습니다.
## Sprint 19 AI Usage

Codex에는 Dynamic Execution Engine의 역할, state schema, step behavior를 구체적으로 명시했습니다. 이를 통해 Codex가 기존 agent interface를 유지하면서 OrchestratorAgent의 직접 실행 로직을 ExecutionEngine으로 이동하도록 활용했습니다.
## Sprint 20 AI Usage

Codex에는 Vector DB를 사용하지 말고 KnowledgeManager와 RetrievalAgent를 먼저 만들라는 제약을 주었습니다. 이를 통해 Codex가 과도한 의존성을 추가하지 않고, JSON 기반 Knowledge Layer와 rule-based retrieval 구조를 구현하도록 활용했습니다.
## Sprint 21 AI Usage

Codex에는 memory schema backward compatibility와 prompt budget 유지를 명시했습니다. 이를 통해 기존 `history.json` 구조가 일부 달라도 crash 없이 검색하고, full history를 prompt에 복사하지 않는 방향으로 구현했습니다.
## Sprint 22 AI Usage

Codex에는 PromptAgent 중심 구조를 role-based prompt orchestration으로 확장하되, generation/evaluation/retry agent는 수정하지 말라는 제약을 명시했습니다. 이를 통해 변경 범위를 prompt 생성 단계로 제한했습니다.
## Sprint22 Detailed AI Usage

Codex was used to refactor prompt generation into section agents while preserving fallback behavior and existing agent interfaces. The prompt explicitly constrained files so generation/evaluation/retry agents stayed untouched.
## Sprint23 AI Usage

Codex was guided with a schema-first prompt: build multi-character handling before UI changes, keep single-image fallback, and do not modify model/tool agents.
## Sprint24 AI Usage

Codex was used to refactor LayoutAgent into a structured composition planner while preserving the existing workflow and generation/evaluation interfaces.
## Sprint25 AI Usage

Codex에는 scene_plan schema와 downstream agent 반영 조건을 명시했습니다. 이를 통해 ScenePlanningAgent가 단순 추가 파일이 아니라 Layout/Pose/Expression/PromptAssembler에 연결되도록 구현했습니다.
## Sprint26 AI Usage

Codex was guided to implement Adapter Pattern while preserving interface stability. This kept provider optimization out of PromptAssembler and GenerationAgent.
## Sprint27 AI Usage

## Sprint30A AI Usage

Codex was used for a constrained refactoring task. The prompt limited allowed files, required backward compatibility, and asked for an incremental migration rather than a full rewrite. This helped keep the workflow stable while improving the architecture.

Codex was guided with explicit provider selection rules and fallback policy. This kept routing deterministic and testable.
