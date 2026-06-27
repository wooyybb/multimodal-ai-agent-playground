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

## Decision 4: 실제 FLUX 연동 전에 Mock Generation을 먼저 구현한 이유

실제 FLUX 연동은 모델 실행 환경, API 비용, 인증 정보, dependency, 이미지 저장 방식 등 여러 외부 변수를 포함합니다.

먼저 PIL 기반 mock generation을 구현하면 `GenerationAgent`의 입력과 출력 계약을 확정하고, `OrchestratorAgent`가 `VisionAgent -> PromptAgent -> GenerationAgent` 순서로 동작하는지 검증할 수 있습니다.

이후 실제 FLUX를 연결할 때는 `FluxTool.generate()` 내부 구현을 교체하는 방식으로 확장할 수 있습니다.

## Decision 5: EvaluationAgent를 별도 Agent로 분리한 이유

이미지 생성과 평가는 서로 다른 책임(responsibility)을 가집니다. `GenerationAgent`는 prompt를 기반으로 이미지를 생성하는 역할에 집중하고, `EvaluationAgent`는 생성 결과가 reference image와 prompt에 얼마나 잘 맞는지 점수화하는 역할에 집중해야 합니다.

평가를 별도 agent로 분리하면 향후 CLIP similarity, DINO similarity, aesthetic score 같은 여러 평가 기준을 독립적으로 확장할 수 있습니다.

또한 평가 결과는 `ReflectionAgent`, `RetryAgent`, `Memory`로 이어지는 feedback loop의 핵심 입력이므로, orchestration 단계에서 명확히 드러나는 별도 agent로 두는 것이 구조적으로 더 적합합니다.

## Decision 6: ReflectionAgent를 별도 Agent로 분리한 이유

`ReflectionAgent`는 평가 결과를 해석하고, 실패 원인과 개선 방향을 제안하는 역할을 가집니다. 이는 prompt 생성이나 image generation과는 다른 feedback responsibility입니다.

별도 agent로 분리하면 향후 rule-based reflection을 LLM 기반 reflection으로 교체하기 쉽습니다. 또한 `EvaluationAgent`의 score, `RetryAgent`의 판단, `Memory`의 과거 기록을 함께 활용하는 확장도 자연스럽습니다.

## Decision 7: Retry 판단을 Threshold 기반으로 시작한 이유

초기 버전에서는 복잡한 정책보다 명확하고 검증 가능한 기준이 중요합니다. `0.75` threshold를 사용하면 score가 일정 기준보다 낮을 때 retry 후보로 표시하는 동작을 쉽게 확인할 수 있습니다.

이 방식은 단순하지만 orchestration contract를 빠르게 안정화할 수 있습니다. 이후에는 score 분포, 사용자 선호, prompt category, memory history를 반영한 동적 threshold로 확장할 수 있습니다.
