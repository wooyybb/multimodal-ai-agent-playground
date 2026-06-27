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
