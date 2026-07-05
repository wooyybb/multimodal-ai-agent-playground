# Architecture

This document describes the responsibility-based architecture of Multimodal AI Agent Playground, including the v1.1 Vision Layer upgrade.

## Target Architecture

```text
User
  |
  v
Planning Layer
  |
  v
Context Layer
  |
  v
Generation Layer
  |
  v
Evaluation Layer
  |
  v
Infrastructure Layer
```

## Layer Responsibilities

| Layer | Responsibility | Internal Examples |
| --- | --- | --- |
| Planning Layer | Understand user intent and reference image. | Vision Router, BLIP, Florence2, Reference Parsing, Goal Planning, Character Extraction, Scene Planning |
| Context Layer | Build generation-ready context. | Character Program, Context Program, Prompt Compilation, Prompt Validation, Prompt Optimization |
| Generation Layer | Generate with provider-specific adaptation. | Provider Router, Provider Adapter, Generation Agent, FLUX |
| Evaluation Layer | Evaluate result and adapt next plan. | Evaluation Aggregator, Reflection, Hypothesis, Strategy, Adaptive Planning, Retry |
| Infrastructure Layer | Support runtime, observability, and access. | Memory, History, Debug Report, Benchmark, FastAPI, Gradio |

## Mermaid Diagram

```mermaid
flowchart TD
    U[User] --> P[Planning Layer]
    P --> C[Context Layer]
    C --> G[Generation Layer]
    G --> E[Evaluation Layer]
    E --> C
    E --> I[Infrastructure Layer]
    P --> I
    C --> I
    G --> I

    P -.internal.-> P1[Vision / Goal / Reference / Scene]
    C -.internal.-> C1[Context Program / Prompt Compiler]
    G -.internal.-> G1[Provider Router / Generation]
    E -.internal.-> E1[Evaluation / Adaptive Planning / Retry]
    I -.internal.-> I1[Memory / Debug / Benchmark / API / UI]
```

## Runtime Flow

1. Planning Layer reads user input and image reference.
2. Context Layer turns planning output into provider-ready context and prompt package.
3. Generation Layer chooses provider and generates the image.
4. Evaluation Layer scores the result and decides whether adaptation or retry is needed.
5. Infrastructure Layer records memory, debug reports, benchmark outputs, and exposes UI/API access.

## Vision Layer v1.1

The Vision Layer no longer treats BLIP as the framework boundary. `VisionAgent` calls `VLMRouter`, and the selected provider returns a shared `vision_result`.

```text
Image
  |
  v
VisionAgent
  |
  v
VLMRouter
  |
  +-- BLIPVLM (default)
  +-- FlorenceVLM (Florence-2 adapter, BLIP fallback)
  +-- QwenVLM (Qwen2.5-VL planned, BLIP fallback)
  |
  v
Standard Vision Result
  |
  v
ReferenceImageParser
```

### Standard Vision Result Schema

Every provider returns these core fields:

```json
{
  "caption": "",
  "detailed_caption": "",
  "objects": [],
  "characters": [],
  "scene": {},
  "style": {},
  "colors": {},
  "composition": {},
  "provider": "",
  "used_fallback": false,
  "latency": 0.0
}
```

Backward-compatible aliases such as `detailed_description`, `character_hints`, and `composition_hints` are still preserved for older downstream components.

### Reference Parsing Priority

`ReferenceImageParser` now reads structured fields first:

```text
characters
-> objects
-> style
-> caption fallback
```

This keeps caption parsing as a fallback while allowing Florence2 or future VLM providers to supply richer visual understanding.

## Reasoning Layer v1.2

The framework keeps rule/mock reasoning as the default, but can optionally call OpenAI through the LLM Layer:

```text
Reasoning Agent
  |
  v
LLMClient / ReasonerRouter
  |
  v
AIModelService
  |
  v
OpenAIProvider
  |
  v
Structured JSON Result
  |
  v
Rule or Mock Fallback if unavailable
```

Existing agents never call OpenAI directly. They call the shared `llm/` layer, which handles provider selection, JSON parsing, fallback metadata, and latency logging.

OpenAI is used only when `LLM_PROVIDER=openai`. If `OPENAI_API_KEY` is missing, the client cannot load, the request fails, or the response is not valid JSON, the system records fallback metadata and returns the existing rule/mock result.

## Design Boundaries

- Agents are internal implementation details.
- Layers are the public explanation model.
- Context Engineering owns the conversion from intent to generation-ready structured data.
- Generation does not own evaluation or retry policy.
- Evaluation owns adaptive planning and retry decision.
- Infrastructure owns memory, debug report, benchmark, API, and UI support.

## Why Responsibility Refactoring?

The project contains many specialized components. Listing every agent makes the framework look more complex than it is. Responsibility-based layers make it easier to understand what the system does and where each capability belongs.

## What Did Not Change

- Core execution order is preserved.
- Existing agents and tools are preserved.
- Florence2 is introduced behind the existing VLM adapter boundary.
- BLIP remains the default and fallback provider.
- OpenAI reasoning is optional and isolated behind the LLM Layer.
- Generation, Evaluation, Adaptive Planning, Memory, FastAPI, Docker, and Benchmark layers are unchanged.

## Future Work

- Continue simplifying ExecutionEngine comments and trace output.
- Organize AgentState fields by layer ownership.
- Add CI smoke tests for compile, import, FastAPI, and Docker.
- Polish demo assets for v1.0 release.
