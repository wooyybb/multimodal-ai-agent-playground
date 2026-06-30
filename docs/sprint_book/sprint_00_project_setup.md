# Sprint 00

## Objective

빈 Python 프로젝트를 Multi-Agent 이미지 생성 프로젝트의 기본 구조로 준비합니다.

## Background

처음부터 모델을 붙이면 구조와 의존성이 섞이기 쉽습니다. 먼저 폴더와 skeleton을 만들어 책임 경계를 잡았습니다.

## Problem

프로젝트가 어떤 agent와 tool로 나뉘는지 아직 드러나지 않았습니다.

## Design Decision

`agents`, `tools`, `workflow`, `memory`, `ui`, `outputs`를 분리했습니다.

## Architecture

```text
agents / tools / workflow / memory / ui / outputs
```

## Implementation Summary

각 Python package에 `__init__.py`를 만들고 TODO skeleton 파일을 생성했습니다.

## AI Agent Concept

초기 agent boundary 설계.

## Prompt Engineering Note

Files Allowed와 생성할 파일 목록을 명확히 지정해 workspace 밖 생성을 방지했습니다.

## Codex Usage

Codex는 scaffold generator로 사용했습니다.

## Debugging Experience

초기에는 기능 검증보다 파일 범위 검증이 중요했습니다.

## Interview Talking Points

- 예상 질문: 왜 먼저 skeleton부터 만들었나요?
- 예상 답변: 모델보다 architecture boundary를 먼저 안정화하기 위해서입니다.
- 꼬리 질문: 이 구조가 나중에 어떤 장점이 있나요?

## Lessons Learned

초기 구조가 이후 sprint의 변경 비용을 줄입니다.

## Future Work

각 skeleton에 mock behavior를 추가합니다.
