# Prompt Engineering

## Prompt Lifecycle

```text
User Prompt
-> Caption
-> Retrieved Context
-> Memory Context
-> Specialist Prompt Sections
-> Context Program
-> Canonical Prompt
-> Prompt Critic
-> Prompt Optimizer
-> Provider Prompt
-> Evaluation Prompt
-> Retry Prompt
```

## Canonical Prompt

Canonical Prompt는 provider에 종속되지 않는 기본 generation prompt입니다. `PromptAssembler`가 character, style, layout, pose, expression, lighting, negative section과 Context Program을 참고해 생성합니다.

## Provider Prompt

Provider Prompt는 특정 generation provider에 맞게 변환된 prompt입니다. `ProviderPromptAdapter`가 FLUX, GPT Image skeleton, SDXL skeleton에 맞춰 변환합니다.

## Evaluation Prompt

Evaluation Prompt는 CLIP 평가용 짧은 prompt입니다. Generation prompt보다 짧고 caption, user intent, 핵심 style/quality keyword만 포함합니다.

## Retry Prompt

Retry Prompt는 ReflectionAgent가 제안한 prompt를 압축한 재시도용 prompt입니다. Generation prompt와 evaluation prompt를 분리해 token overflow를 방지합니다.

## Context Program

Context Program은 prompt 자체가 아니라 prompt를 만들기 위한 structured source of truth입니다.

```text
task
user_goal
scene
characters
style
layout
pose
expression
lighting
quality
negative
memory
retrieval
provider
output
```

`PromptAssembler`와 `ProviderPromptAdapter`는 Context Program 전체를 prompt에 복사하지 않고, provider가 이해할 visual instruction만 추출합니다.

## Prompt Design Pattern

Sprint prompt는 보통 다음 순서를 사용합니다.

```text
Task
-> Architecture
-> Workspace Rule
-> Files Allowed
-> Files Forbidden
-> Requirements
-> Documentation
-> Done Definition
```

## Future Work

- Prompt template library
- Provider-specific prompt tests
- LLM prompt optimizer integration
- Context Program v2 prompt compiler

## Prompt Critique

Prompt critique is split into two layers:

- Rule-based critique checks duplicate keywords, missing sections, warnings, and quality score.
- Semantic mock/future LLM critique checks conflicts, priority issues, provider suitability, and intent mismatch.

The critic does not rewrite prompts. It creates structured reports so optimizer agents can decide what to change.
