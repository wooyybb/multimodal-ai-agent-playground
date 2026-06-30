# Sprint 05

## Objective

`EvaluationAgent`와 `ClipTool`을 연결해 생성 결과를 score로 평가합니다.

## Background

retry와 reflection이 의미 있으려면 정량 평가 signal이 필요합니다.

## Problem

초기에는 실제 CLIP 없이 score contract를 만들어야 했습니다.

## Design Decision

파일 존재 여부와 prompt 길이를 활용한 deterministic mock score를 사용했습니다.

## Architecture

```text
generated_image + final_prompt -> EvaluationAgent -> ClipTool -> score
```

## Implementation Summary

0.0~1.0 score를 반환하고 Orchestrator result에 포함했습니다.

## AI Agent Concept

Model-based Evaluation.

## Prompt Engineering Note

실제 CLIP 금지, mock score, deterministic behavior를 명시했습니다.

## Codex Usage

Codex는 evaluation interface와 logging을 구현했습니다.

## Debugging Experience

score가 retry decision의 기준점으로 쓰일 수 있음을 확인했습니다.

## Interview Talking Points

- 예상 질문: EvaluationAgent는 왜 분리했나요?
- 예상 답변: generation과 evaluation은 다른 책임이기 때문입니다.
- 꼬리 질문: score는 어떻게 개선할 수 있나요?

## Lessons Learned

평가 agent는 feedback loop의 출발점입니다.

## Future Work

실제 CLIP image-text similarity로 확장합니다.
