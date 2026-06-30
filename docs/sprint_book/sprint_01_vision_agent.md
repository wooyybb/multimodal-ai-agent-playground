# Sprint 01

## Objective

`VisionAgent`가 이미지를 caption으로 변환하는 구조를 만듭니다.

## Background

이미지 생성 workflow는 입력 이미지를 언어 정보로 변환해야 downstream prompt generation이 가능합니다.

## Problem

처음부터 BLIP를 붙이면 dependency와 모델 로딩 문제가 architecture 학습을 방해할 수 있습니다.

## Design Decision

`VisionAgent`는 `BlipTool`만 호출하고, 초기에는 mock caption을 반환했습니다.

## Architecture

```text
VisionAgent -> BlipTool -> caption
```

## Implementation Summary

`VisionAgent.run(image)`와 `BlipTool.generate_caption(image)` interface를 만들었습니다.

## AI Agent Concept

Tool-Agent Separation.

## Prompt Engineering Note

실제 BLIP 금지, mock caption, logging 요구를 명시했습니다.

## Codex Usage

Codex는 agent-tool interface를 빠르게 구성하는 데 사용했습니다.

## Debugging Experience

mock caption으로 pipeline 연결을 먼저 검증했습니다.

## Interview Talking Points

- 예상 질문: 왜 BLIP를 바로 붙이지 않았나요?
- 예상 답변: 먼저 interface contract를 안정화하기 위해 mock-first로 개발했습니다.
- 꼬리 질문: 나중에 실제 BLIP로 바꿀 때 어디를 수정하나요?

## Lessons Learned

모델 교체 가능성은 tool layer에 숨기는 것이 좋습니다.

## Future Work

`BlipTool`에 실제 BLIP captioning을 연결합니다.
