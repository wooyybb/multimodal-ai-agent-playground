# Prompt Engineering

이번 Sprint prompt는 Architecture Prompt입니다. 단순히 함수 구현을 요청한 것이 아니라, Reflection 기반 Self-Improving AI Agent 구조를 어떤 순서와 책임으로 발전시킬지 정의했습니다.

## Pattern

```text
Task
↓
Architecture
↓
Workspace
↓
Allowed Files
↓
Forbidden Files
↓
Requirements
↓
Documentation
↓
Done Definition
```

이 구조는 Codex가 임의로 범위를 넓히지 않도록 도와줍니다. 특히 allowed files와 forbidden files를 분리하면 README, main, requirements 같은 파일을 실수로 수정하는 일을 줄일 수 있습니다.

## 왜 Architecture Prompt인가

이번 작업의 핵심은 `ReflectionAgent`, `RetryAgent`, `Memory`를 단순히 추가하는 것이 아니라 feedback loop의 책임 분리를 설계하는 것입니다.

따라서 prompt는 구현 상세보다 agent 순서, 책임, 저장 데이터, 문서화 기준을 먼저 정의했습니다.

## Sprint 7 Memory Engineering Prompt

이번 prompt도 Architecture Prompt입니다. 목표는 단순히 `history.json`을 저장하는 것이 아니라, AI Agent의 memory 구조를 Working Memory, Episodic Memory, State Management, Agent Context, Memory Interface 관점에서 설계하는 것이었습니다.

특히 다음 순서가 명확했습니다.

```text
Task
↓
Architecture
↓
Workspace
↓
Allowed Files
↓
Forbidden Files
↓
Requirements
↓
Documentation
↓
Done Definition
```

이 패턴은 Codex가 구현 범위를 벗어나지 않고, 코드와 문서를 같은 architecture decision에 맞춰 업데이트하도록 돕습니다.

## Codex Prompt Template 구성요소

- Task: 이번 Sprint에서 달성할 구체적 작업
- Learning Objective: 기능보다 학습해야 할 engineering concept
- Why: 변경이 필요한 배경과 문제 정의
- Architecture: current structure와 target structure
- Files Allowed: 수정 또는 생성 가능한 파일 범위
- Files Forbidden: 절대 수정하지 않을 파일
- Requirements: class, method, schema, logging 요구사항
- Documentation: 반드시 업데이트할 문서 목록
- Done Definition: 실행 검증과 완료 기준

## Sprint 8 Retry Loop Prompt

Sprint 8 prompt는 무한 loop를 방지하기 위한 제약이 명확한 Architecture Prompt입니다. 핵심 제약은 `RetryAgent`가 판단만 하고, `OrchestratorAgent`가 loop를 제어한다는 점입니다.

이 제약 덕분에 retry policy와 workflow execution 책임이 분리됩니다. 또한 one-step retry로 제한해 infinite loop, 과도한 파일 생성, 복잡한 state transition을 피할 수 있습니다.

## Sprint 9 Gradio UI Prompt

Sprint 9 prompt는 UI와 Agent 책임 분리를 명확히 하기 위한 Architecture Prompt입니다. 핵심 제약은 UI가 agent를 직접 호출하지 않고 `MultimodalPipeline`만 호출한다는 점입니다.

또한 수정 가능한 파일과 금지 파일을 분리해 UI 작업이 agent implementation이나 model dependency를 건드리지 않도록 제한했습니다. 이 제약은 demo UI를 빠르게 연결하면서도 backend workflow의 책임 경계를 유지하게 합니다.

## Sprint 10 Real BLIP Prompt

Sprint 10 prompt는 실제 모델 통합의 위험을 줄이기 위해 제약을 명확히 둔 prompt입니다. 수정 가능한 파일을 `BlipTool`, `VisionAgent`, `requirements.txt`, docs로 제한해 UI, orchestrator, memory, generation/evaluation 코드를 건드리지 않도록 했습니다.

또한 fallback caption과 lazy loading을 명시해 model dependency, network cache, device 문제로 전체 workflow가 깨지는 위험을 줄였습니다.

## Sprint 11 Real FLUX Prompt

Sprint 11 prompt는 실제 API 통합의 실패 가능성을 줄이기 위해 fallback, environment variable, files forbidden을 명확히 둔 prompt입니다.

`HF_TOKEN`을 환경변수로 사용하도록 제한해 보안 정보를 코드에 넣지 않게 했고, API 실패 시 fallback mock image를 생성하도록 요구해 workflow 안정성을 유지했습니다. 또한 UI, orchestrator, memory를 금지 파일로 지정해 generation backend 교체가 agent workflow를 흔들지 않게 했습니다.

## Sprint 12 Real CLIP Prompt

Sprint 12 prompt는 실제 model-based evaluation을 추가하면서도 interface 안정성을 유지하도록 설계했습니다.

`EvaluationAgent.run(reference_image, generated_image_path, final_prompt)` interface를 유지하고, CLIP internals는 `ClipTool`로 제한했습니다. fallback score, lazy loading, files forbidden을 명시해 모델 로딩 실패나 inference 오류가 전체 workflow를 멈추지 않도록 했습니다.

## Sprint 13 Validation Prompt

Sprint 13 prompt는 기능 추가를 제한하고 validation, documentation, stability 개선을 명시한 prompt입니다.

Allowed files와 forbidden files를 분리해 tools와 requirements를 건드리지 않도록 했고, testing docs, known issues, demo script를 Done Definition에 포함해 demo readiness를 높였습니다.

## Sprint 15 PlannerAgent Prompt

Sprint 15 prompt는 Planner와 Orchestrator의 책임 분리를 명확히 하기 위한 Architecture Prompt입니다.

핵심 제약은 `PlannerAgent`가 계획만 만들고, `OrchestratorAgent`가 기존 workflow를 계속 실행한다는 점입니다. 또한 dynamic execution engine을 이번 Sprint 범위에서 제외해 E2E 안정성을 유지했습니다.

## Sprint 16 ToolRegistry Prompt

Sprint 16 prompt는 architecture-changing task에서 수정 가능한 파일과 금지 파일을 분리해 기존 E2E 동작을 보호했습니다.

특히 Tool 이름과 Planner execution_plan 이름을 맞추도록 명시해 향후 dynamic execution engine으로 확장할 기반을 만들었습니다. 동시에 이번 Sprint에서는 완전한 dynamic engine을 금지해 registry 기반 호출 구조만 안전하게 도입했습니다.

## Sprint 17 Context Engineering Prompt

Sprint 17 prompt는 PromptAgent와 OrchestratorAgent의 책임 분리를 명확히 했습니다. PromptAgent가 MemoryManager나 PlannerAgent를 직접 호출하지 않고, Orchestrator가 context dict를 구성해 전달하도록 제한했습니다.

또한 `context`를 선택 인자로 둬 기존 `run(caption, user_prompt)` 호출이 깨지지 않게 했습니다. 이는 backward compatibility를 유지하면서 context-aware prompt building으로 확장하기 위한 설계입니다.
## Sprint 18 Prompt Compression Strategy

이번 Sprint의 prompt는 Architecture Prompt입니다. Task, Architecture, Workspace, Allowed Files, Forbidden Files, Requirements, Documentation, Done Definition 순서로 구성되어 Codex가 구현 범위와 설계 의도를 동시에 이해하도록 했습니다.

핵심 전략은 raw context를 prompt에 붙이지 않고, `PromptCompressor`를 통해 `task`, `planner_hint`, `style_hint`, `history_hint` 같은 짧은 hint로 변환하는 것입니다.
## Sprint 19 Prompt Engineering

이번 prompt는 architecture refactoring prompt입니다. 기존 E2E workflow를 유지하면서 실행 책임만 OrchestratorAgent에서 DynamicExecutionEngine으로 옮기도록, `State Schema`, `Step Behavior`, `Error Handling`, `Done Definition`을 명확히 제시했습니다.

이 구조 덕분에 Codex는 UI, memory, tool interface를 건드리지 않고 실행 계층만 분리할 수 있었습니다.
## Sprint 20 Prompt Engineering

이번 Sprint prompt는 Knowledge Layer를 설계하기 위한 architecture prompt입니다. 핵심은 PromptAgent에 rule을 직접 넣지 않고, KnowledgeManager -> RetrievalAgent -> PromptCompressor -> PromptAgent 흐름으로 knowledge augmentation을 분리하는 것이었습니다.

Vector DB를 금지한 제약은 오히려 RAG의 본질인 retrieval responsibility와 augmentation responsibility를 명확히 드러내는 데 도움이 되었습니다.
## Sprint 21 Prompt Engineering

이번 Sprint prompt는 memory retrieval의 위치와 prompt budget 제한을 명확히 지정했습니다. `memory_retrieval`은 caption을 활용하기 위해 `vision` 이후에 배치했고, 검색 결과 전체가 아니라 짧은 hint만 PromptCompressor에 전달하도록 설계했습니다.
## Sprint 22 Prompt Engineering

이번 Sprint는 prompt engineering을 하나의 함수가 아니라 여러 역할 기반 agent의 협업으로 설계했습니다. Character, Style, Layout, Lighting, Negative Prompt를 분리하고 PromptAssembler가 final generation prompt를 만들도록 했습니다.
## Sprint22 Detailed Prompt Engineering

Long manual prompt programs are decomposed into section prompts: character, style, layout, pose, expression, lighting, and negative prompt. This turns prompt writing into prompt orchestration.
## Sprint23 Prompt Engineering

Character preservation prompt is decomposed into structured character schema and compact generation prompt rules. The goal is to preserve identity without repeating long prompt sentences.
## Sprint24 Prompt Engineering

Layout prompt는 단순히 `photobooth`나 `vertical`을 붙이는 방식에서 벗어나 frame structure, camera view, subject placement, background style, composition rules로 분해했습니다.
## Sprint25 Prompt Engineering

이번 Sprint는 사용자 자연어를 바로 prompt로 만들지 않고 Scene Plan이라는 중간 표현으로 변환합니다. 이 방식은 prompt를 더 구조적으로 만들고, Layout/Pose/Expression agent가 같은 장면 해석을 공유하게 합니다.
## Sprint26 Prompt Engineering

Canonical prompt is transformed into provider-specific prompt. FLUX adapter removes internal planning/debug terms and keeps visual keywords around subject, style, layout, lighting, pose, expression, and composition.
## Sprint27 Prompt Engineering

Provider별 prompt 최적화와 provider routing을 분리했습니다. Routing은 provider 선택을 담당하고, Adapter는 선택된 provider에 맞는 prompt 변환을 담당합니다.

## Sprint30A Prompt Engineering

이번 Prompt는 대규모 refactoring을 요청하면서도 `incremental refactoring`과 `backward compatibility`를 명시했습니다. 이는 Codex가 모든 Agent를 한 번에 바꾸지 않고, 지정된 Agent만 안전하게 state-based interface로 전환하도록 범위를 제한하기 위함입니다.

## Sprint31 Prompt Engineering

이번 Prompt는 prompt quality analysis 결과를 실제 prompt repair로 연결하는 Critic-Optimizer 패턴을 명시했습니다. 특히 internal context를 generation prompt에서 제거하도록 요구하여, workflow metadata가 이미지 생성 지시문에 섞이지 않게 했습니다.

## Sprint33 Prompt Engineering

이번 Prompt는 LLM optimizer를 바로 구현하기보다 prompt reasoning layer의 interface를 먼저 설계하도록 했습니다. disabled/mock/fallback mode를 요구한 이유는 API key나 외부 provider 없이도 prompt optimization 흐름을 검증하기 위해서입니다.
