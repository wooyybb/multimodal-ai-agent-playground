# Sprint 12: Real CLIP Evaluation

## Problem

`EvaluationAgent`가 mock score만 반환하여 실제 자동 평가 경험을 보여주기 어려웠습니다.

## Decision

`ClipTool`에 `openai/clip-vit-base-patch32` 기반 image-text similarity evaluation을 추가합니다.

## Alternatives

- Mock score 유지
- DINO image similarity 사용
- Aesthetic score 사용
- Human preference only

## Reason

CLIP은 이미지와 텍스트를 같은 embedding space에서 비교할 수 있어 생성 결과와 prompt의 alignment를 평가하는 MVP에 적합합니다.

## Future Work

Reference image similarity, DINO similarity, aesthetic score, human preference evaluation으로 확장할 수 있습니다.
