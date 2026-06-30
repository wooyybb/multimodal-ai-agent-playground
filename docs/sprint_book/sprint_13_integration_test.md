# Sprint 13

## Objective

새 기능 추가보다 End-to-End validation과 demo readiness를 정리합니다.

## Background

여러 agent와 real tool이 연결되었지만 전체 흐름 검증이 필요했습니다.

## Problem

UI, memory, output, trace가 모두 안정적으로 이어지는지 문서화가 부족했습니다.

## Design Decision

testing, known issues, demo script를 만들고 UI/Memory 안정성을 보강했습니다.

## Architecture

```text
UI -> Pipeline -> Orchestrator -> Agents -> Memory -> UI Output
```

## Implementation Summary

None output handling, score formatting, agent_trace formatting, memory save failure 방어를 추가했습니다.

## AI Agent Concept

End-to-End Validation.

## Prompt Engineering Note

기능 추가를 제한하고 validation docs를 Done Definition에 포함했습니다.

## Codex Usage

Codex는 테스트 문서화와 안정성 점검에 사용했습니다.

## Debugging Experience

demo readiness는 코드보다 설명, 한계, 체크리스트가 중요했습니다.

## Interview Talking Points

- 예상 질문: E2E 테스트는 어떻게 했나요?
- 예상 답변: UI 입력부터 memory 기록까지 체크리스트로 검증했습니다.
- 꼬리 질문: known issues를 왜 문서화했나요?

## Lessons Learned

포트폴리오 완성도는 기능 개수보다 검증 가능성에 달려 있습니다.

## Future Work

자동 smoke test와 demo video를 추가합니다.
