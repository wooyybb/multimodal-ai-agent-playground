# Decisions

## Decision 1: Pipeline-Only 구조가 아니라 OrchestratorAgent를 도입한 이유

초기에는 `workflow/pipeline.py`에서 `VisionAgent`와 `PromptAgent`를 직접 호출하는 단일 파이프라인(Single Pipeline) 구조였습니다.

하지만 프로젝트의 목표는 여러 전문 agent가 협력하는 멀티 에이전트 시스템(Multi-Agent System)입니다. 따라서 agent 간 실행 순서, trace, 향후 retry loop와 memory 연결을 관리할 별도 조정자(coordinator)가 필요했습니다.

`OrchestratorAgent`를 도입하면 workflow는 전체 실행 진입점(entry point) 역할에 집중하고, agent coordination은 orchestrator가 담당할 수 있습니다.

## Decision 2: 실제 모델 연결 전에 Mock 기반으로 개발하는 이유

BLIP, FLUX, CLIP 같은 실제 AI model은 설치, 실행 환경, GPU, API key, dependency 이슈가 생길 수 있습니다.

프로젝트 초반에는 model 성능보다 전체 구조와 data flow가 더 중요합니다. Mock 기반으로 먼저 개발하면 agent 간 입출력 계약(interface)을 빠르게 검증할 수 있습니다.

이 방식은 나중에 실제 model을 연결할 때도 기존 구조를 크게 바꾸지 않고 tool 내부 구현만 교체할 수 있게 해줍니다.

## Decision 3: LangGraph/CrewAI 없이 Python Class 기반으로 시작하는 이유

LangGraph, CrewAI, AutoGen 같은 framework는 강력하지만, 초기 학습 및 포트폴리오 단계에서는 추상화가 너무 빨리 커질 수 있습니다.

현재 프로젝트는 multi-agent 개념, orchestration 흐름, agent responsibility를 명확히 보여주는 것이 우선입니다.

따라서 단순한 Python class 기반으로 시작해 구조를 직접 이해하고, 필요해지는 시점에 framework 도입을 검토하는 방향을 선택했습니다.
