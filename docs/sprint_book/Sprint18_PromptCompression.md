# Sprint 18

## Objective

PromptAgent가 raw context를 그대로 prompt에 붙이지 않고, PromptCompressor를 통해 압축된 context만 사용하도록 개선한다.

## Background

Sprint 17에서 context-aware PromptAgent를 만들었지만, Planner reason과 previous best prompt가 길어질수록 final prompt가 과도하게 길어질 수 있었다.

## Problem

CLIP text encoder는 일반적으로 짧은 text budget을 가진다. 긴 prompt는 `Sequence length must be less than max_position_embeddings (77)` 같은 문제를 만들 수 있다.

## Design Decision

`PromptCompressor`를 별도 class로 추가했다. Context Builder는 정보를 수집하고, PromptCompressor는 필요한 정보만 선택하고, PromptAgent는 최종 prompt를 만든다.

## Architecture

```text
PlannerAgent
-> Context Builder
-> PromptCompressor
-> PromptAgent
-> GenerationAgent
-> EvaluationAgent
```

## Implementation Summary

- `agents/prompt_compressor.py` 추가
- `OrchestratorAgent`에 `prompt_compressor` registry 등록
- `PromptAgent`가 `compressed_context`만 사용하도록 변경
- prompt 길이를 60 words 이하로 제한

## AI Agent Concept

이번 Sprint의 핵심은 Context Engineering이다. 좋은 agent는 모든 정보를 prompt에 넣는 것이 아니라, 실행 목적에 필요한 정보만 선택하고 압축한다.

## Prompt Engineering Note

raw planner result와 full memory를 prompt에 직접 넣지 않는 규칙을 만들었다.

## Codex Usage

Codex는 허용 파일 범위 안에서 PromptCompressor 설계, Orchestrator 연결, 문서 업데이트를 수행했다.

## Debugging Experience

긴 prompt가 CLIP token limit과 충돌할 수 있다는 점을 기준으로 prompt budget을 명시적으로 도입했다.

## Interview Talking Points

Q. 왜 Prompt Compression이 필요한가요?
A. Agent가 사용하는 context가 늘어날수록 prompt가 길어지고 모델 입력 제한을 초과할 수 있기 때문이다.

Q. Context Budget은 무엇인가요?
A. 모델에 전달할 수 있는 context의 양을 제한하고, 중요한 정보만 선택하는 설계 기준이다.

## Lessons Learned

Context는 많이 넣는 것보다 잘 고르는 것이 중요하다.

## Future Work

- RAG Style Library
- Semantic Memory
- token-aware prompt builder
