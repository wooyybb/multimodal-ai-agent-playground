# Sprint 22: Prompt Orchestration Framework

## Problem

PromptAgent 하나가 caption, retrieval, memory, planner context, user prompt를 모두 처리하면서 책임이 커졌다.

## Decision

Prompt 생성 책임을 Character, Style, Layout, Lighting, Negative Prompt, Assembly agent로 분리했다.

## Alternatives

- 기존 PromptAgent 유지
- PromptCompressor에 모든 조립 책임 추가
- LLM 하나로 prompt 생성
- 외부 prompt template engine 도입

## Reason

역할별 agent로 나누면 prompt engineering 과정을 설명하고 디버깅하기 쉽다. 또한 향후 특정 prompt 영역만 개선하거나 교체하기 쉽다.

## Future Work

- PromptRouter 추가
- role output schema validation
- LLM 기반 fragment generation
- A/B prompt assembly experiments
## Detailed Update

Sprint22 now includes PoseAgent and ExpressionAgent. Negative prompt is separated from generation prompt and stored as its own state field for future provider-specific routing.
