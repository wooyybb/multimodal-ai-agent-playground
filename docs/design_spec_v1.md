# Multimodal AI Agent Playground

## Design Specification v1.0

## 1. Project Goal

Reference Image를 이해하고, Context Engineering 기반으로 Prompt를 생성하며, 생성 결과를 자동 평가하고, Adaptive Planning을 통해 반복 개선하는 멀티모달 AI Agent Framework를 구축한다.

## 2. Design Philosophy

- Model Independent
- Provider Independent
- Layer-based Architecture
- Explainable Agent Workflow
- Context-first Generation

## 3. Architecture

```text
Planning Layer
↓
Context Layer
↓
Generation Layer
↓
Evaluation Layer
↓
Reasoning Layer
↓
Memory / Observability
```

## 4. Core Components

### Planning

- Vision Agent
- Reference Parser
- Planner

### Context

- Character Program
- Context Program
- Prompt Compiler

### Generation

- Provider Router
- Provider Adapter
- Generation Agent

### Evaluation

- Evaluation Aggregator
- CLIP Metric
- Reflection

### Reasoning

- Adaptive Planning

### Infrastructure

- Memory
- Benchmark
- FastAPI
- Gradio

## 5. Execution Flow

```text
Input Image
↓
Vision Understanding
↓
Reference Parsing
↓
Context Program
↓
Prompt Compilation
↓
Generation
↓
Evaluation
↓
Reflection
↓
Adaptive Planning
↓
Retry (Optional)
```

## 6. Current Providers

### Vision

- BLIP (default)
- Florence2 (adapter, BLIP fallback when unavailable)
- Qwen2.5-VL (planned, BLIP fallback)

All vision providers return a Standard Vision Result with `caption`, `detailed_caption`, `objects`, `characters`, `scene`, `style`, `colors`, `composition`, `provider`, `used_fallback`, and `latency`.

### Generation

- FLUX (default)

### Reasoning

- Rule-based
- OpenAI Ready

### Evaluation

- CLIP
- Rule Metrics

## 7. Current Status

This design specification describes the v1.0 release-candidate baseline.

| Area | Status |
| --- | --- |
| Version | v1.0 RC baseline |
| Framework | Stable |
| API | Stable |
| Gradio | Stable |
| FastAPI | Stable |
| Docker | Prepared |
| GitHub Actions | Planned |

## 8. Future

| Version | Focus |
| --- | --- |
| v1.1 | Real VLM |
| v1.2 | Real LLM |
| v1.3 | Advanced Evaluation |
| v2.0 | Video Agent |
| v3.0 | Physical AI |
