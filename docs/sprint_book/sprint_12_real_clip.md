# Sprint 12

## Objective

mock score를 CLIP image-text similarity score로 확장합니다.

## Background

자동 평가와 retry loop에는 model-based evaluation이 필요했습니다.

## Problem

EvaluationAgent가 mock score만 반환했습니다.

## Design Decision

`ClipTool`에서 CLIP feature tensor를 추출하고 cosine similarity를 계산했습니다.

## Architecture

```text
EvaluationAgent -> ClipTool -> CLIP image/text features -> score
```

## Implementation Summary

`get_image_features`, `get_text_features`, `F.normalize`, cosine score 변환을 구현했습니다.

## AI Agent Concept

Multimodal Embedding Evaluation.

## Prompt Engineering Note

BaseModelOutput을 tensor처럼 쓰지 말고 feature API만 쓰도록 명시했습니다.

## Codex Usage

Codex는 CLIP tensor extraction bug fix와 문서화를 수행했습니다.

## Debugging Experience

`BaseModelOutputWithPooling`은 feature tensor가 아니라는 점을 확인했습니다.

## Interview Talking Points

- 예상 질문: CLIP score는 무엇인가요?
- 예상 답변: image/text embedding의 cosine similarity를 0~1로 변환한 alignment score입니다.
- 꼬리 질문: CLIP score의 한계는?

## Lessons Learned

모델 output object와 feature tensor를 구분해야 합니다.

## Future Work

reference image similarity와 aesthetic score를 추가합니다.
