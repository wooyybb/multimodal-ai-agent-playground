# Sprint 09

## Objective

Multi-agent workflow를 Gradio UI에 연결합니다.

## Background

코드 내부 workflow만으로는 portfolio demo를 보여주기 어렵습니다.

## Problem

사용자가 직접 이미지와 prompt를 입력하고 결과를 확인할 수 없었습니다.

## Design Decision

UI는 agent를 직접 호출하지 않고 `MultimodalPipeline`만 호출하게 했습니다.

## Architecture

```text
Gradio UI -> MultimodalPipeline -> OrchestratorAgent -> UI Output
```

## Implementation Summary

caption, final prompt, image, score, reflection, retry, trace를 UI에 표시했습니다.

## AI Agent Concept

Human-in-the-loop Interface.

## Prompt Engineering Note

UI 책임과 agent 책임을 분리하도록 Files Forbidden을 강하게 지정했습니다.

## Codex Usage

Codex는 Gradio Blocks UI와 output binding을 구현했습니다.

## Debugging Experience

None output과 error message 처리가 UI 안정성에 중요했습니다.

## Interview Talking Points

- 예상 질문: 왜 Gradio를 사용했나요?
- 예상 답변: 이미지 입력과 생성 결과 demo를 빠르게 만들 수 있기 때문입니다.
- 꼬리 질문: UI가 agent를 직접 호출하지 않는 이유는?

## Lessons Learned

UI는 orchestration을 알지 않아야 유지보수가 쉽습니다.

## Future Work

history viewer와 demo assets를 추가합니다.
