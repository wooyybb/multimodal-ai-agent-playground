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
