# Multimodal AI Agent Playground

**Responsibility-based AI Agent Framework for Multimodal Image Generation**

![Status](https://img.shields.io/badge/status-v1.1-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)
![Architecture](https://img.shields.io/badge/Architecture-Responsibility--Layered-purple)
![FastAPI](https://img.shields.io/badge/API-FastAPI-teal)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange)

## Project Overview

This project is not about having many agents. It is a multimodal image generation framework organized by responsibility.

The framework is explained through five layers:

1. Planning Layer
2. Context Layer
3. Generation Layer
4. Evaluation Layer
5. Infrastructure Layer

Each internal agent is treated as an implementation detail inside one of these layers.

## Why This Project?

Most image generation demos are direct prompt-to-image scripts. They are hard to inspect when the result is poor.

This project separates the workflow into responsibilities:

```text
Understand intent and reference image
-> Build generation-ready context
-> Generate with provider-specific adaptation
-> Evaluate and adapt the plan
-> Save memory, debug reports, and benchmark results
```

The goal is to make the system understandable in five minutes: what each layer owns, how data moves, and where future improvements belong.

## Layer-based Architecture

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

## End-to-End Workflow

| Step | Layer | Responsibility |
| --- | --- | --- |
| 1 | Planning | Understand user intent, reference image, goal, character, and scene. |
| 2 | Context | Build Context Program, validate it, optimize prompt, and compile provider prompt package. |
| 3 | Generation | Route provider, adapt prompt, and generate image. |
| 4 | Evaluation | Evaluate output, reflect, select strategy, adapt plan, and decide retry. |
| 5 | Infrastructure | Save memory, debug report, benchmark output, API/UI access, and run history. |

## Core Layers

### Planning Layer

Responsible for understanding user intent and reference image.

Includes vision, goal planning, reference parsing, character extraction, and scene planning.

The Vision Layer is provider-independent:

```text
Image
  |
  v
Vision Router
  |
  +-- BLIP (default)
  +-- Florence-2 (optional, BLIP fallback if unavailable)
  |
  v
Standard Vision Result
  |
  v
Reference Image Parser
```

All vision providers return the same `vision_result` contract: `caption`, `detailed_caption`, `objects`, `characters`, `scene`, `style`, `colors`, `composition`, `provider`, `model`, `used_fallback`, and `latency`.

Florence-2 is treated as a Vision Parser, not only a caption model:

```text
Florence Task Router
  +-- <CAPTION>
  +-- <DETAILED_CAPTION>
  +-- <OD>
  +-- OCR skeleton
  |
  v
Structured Vision Result
```

`ReferenceImageParser` prioritizes structured object detection results first, then `detailed_caption`, then `caption`, and finally rule-based fallback parsing. Detected objects are normalized as `{name, bbox}` records so accessories such as weapons, hats, and bags can be carried into the reference image context.

### Context Layer

Responsible for making generation-ready context.

Externally, this layer can be understood as the Prompt Compiler layer. Internally, it includes Context Program, prompt validation, negative prompt, prompt optimization, and prompt compression.

v2.5 adds Long Prompt Structuring for reference-aware style transfer. Long user prompts are no longer copied directly into the final prompt. They are first converted into a `style_transfer_program`, then rendered into provider-specific prompts.

```text
Long User Prompt
  |
  v
Style Transfer Program
  |
  v
Prompt Sanitizer / Prompt Validator
  |
  +-- FLUX dense prompt
  +-- SDXL short style prompt
  +-- CLIP semantic summary
  +-- negative prompt
```

The Prompt Sanitizer gives user forbidden intent the highest priority. For example, if the user asks to remove weapons, terms such as `weapon`, `sword`, `blade`, `combat stance`, and `holding a sword` are removed from generation-facing prompts even if the reference caption contains them. The Prompt Validator checks whether forbidden concepts survived, duplicate phrases remain, and SDXL/CLIP prompts stay under the 77-token budget.

### Generation Layer

Responsible for provider-specific generation.

It includes provider routing, provider prompt adaptation, generation planning, generation routing, and provider-specific generation.

v2.0 adds two generation modes:

| Mode | Route | Purpose |
| --- | --- | --- |
| Fast Mode | `flux_fast` -> FLUX | Keep the existing lightweight FLUX path. |
| Quality Mode | `sdxl_quality` -> SDXL Img2Img | Use the reference image through Diffusers `StableDiffusionXLImg2ImgPipeline`. |

Quality Mode uses a real Diffusers SDXL Img2Img backend. It loads `StableDiffusionXLImg2ImgPipeline`, resizes the reference image to the configured resolution, and generates from `prompt + reference_image + strength`.

v2.2 keeps FLUX as the default provider and adds real SDXL Img2Img integration. `GENERATION_PROVIDER=flux_fast` selects Fast Mode, while `GENERATION_PROVIDER=sdxl_quality` selects Quality Mode. SDXL records `model_id`, `resolution`, `steps`, `cfg`, `strength`, `latency`, prompt length, `generation_is_mock=false`, and `fallback_reason` in the debug report. If the SDXL model cannot be loaded or the reference image is missing, the provider returns a clear error status and does not create a mock image. The FLUX fast path is unchanged.

SDXL Img2Img requires `diffusers` and `accelerate`. They are listed in `requirements.txt`; if your local environment reports an accelerate-related loading error, reinstall the runtime dependencies:

```bash
pip install -r requirements.txt
```

Test-only mock output is disabled by default. It is only allowed when `ALLOW_MOCK_GENERATION=true`, and debug reports record `generation_is_mock`, `fallback_reason`, `generation_error_type`, `generation_error_repr`, `generation_error_stage`, and `generation_error_traceback`.

v2.1 adds a Reference Conditioning Interface. Current generation is still prompt-only, but the Prompt Compiler now creates a `reference_conditioning_package` that future providers can use for img2img, IP-Adapter, or ControlNet.

Prompt-only generation has limits for reference preservation: text can describe hair color, eye color, outfit, identity, and accessories, but it cannot directly bind visual features from the reference image. The conditioning package keeps those preservation requirements explicit until real reference-conditioned providers are attached.

v2.3 adds provider-specific prompt rendering. FLUX keeps the dense generation prompt. SDXL Img2Img receives a short Style Prompt generated only from `style_program`: style, lighting, quality, mood, camera, rendering, and color palette. Identity terms such as gender, hair, outfit, eye color, and accessories are removed because the reference image supplies identity through Img2Img.

v2.4 connects optional IP-Adapter conditioning inside the SDXL Img2Img provider. SDXL Img2Img preserves reference structure, IP-Adapter strengthens identity/reference feature preservation, and the Style Prompt controls style direction. The adapter is inference-only; no training is performed. The default adapter config uses `IP_ADAPTER_REPO_ID=h94/IP-Adapter`, `IP_ADAPTER_SUBFOLDER=sdxl_models`, and `IP_ADAPTER_WEIGHT_NAME=ip-adapter_sdxl.bin`. If adapter loading fails, the provider falls back to SDXL Img2Img without crashing and records the fallback reason in the debug report.

v2.6 adds a Style Transfer Preset Manager. SDXL Img2Img no longer uses one fixed `strength`, IP-Adapter scale, CFG, and step count for every style. The framework selects a `generation_preset` from the `style_transfer_program`, such as `photobooth_soft`, `ugly_cute_drawing`, `anime_webtoon`, or `realistic_preserve`.

The trade-off is explicit:

- Lower Img2Img `strength` keeps the original reference stronger.
- Higher Img2Img `strength` allows stronger style change but can distort identity.
- Higher IP-Adapter scale preserves reference identity/features more strongly.
- Lower IP-Adapter scale gives the style prompt more freedom.
- CFG and steps control prompt guidance strength and generation refinement.

Environment variables can override the preset when manual tuning is needed: `SDXL_STRENGTH`, `IP_ADAPTER_SCALE`, `SDXL_CFG`, `SDXL_STEPS`, `SDXL_WIDTH`, and `SDXL_HEIGHT`.

### Evaluation Layer

Responsible for output evaluation and adaptive planning.

It includes evaluation aggregation, reflection, hypothesis/strategy logic, adaptive planning, and retry decision. Hypothesis, Strategy, and Retry are treated as internal steps of adaptive evaluation.

### Infrastructure Layer

Responsible for system support.

It includes memory, history, debug report, benchmark, report generator, FastAPI, and Gradio.

## Key Features

- Responsibility-based framework architecture
- DynamicExecutionEngine with layer-readable execution flow
- ToolRegistry with layer metadata
- Provider-independent Vision Layer with BLIP default and Florence-2 fallback support
- Florence Task Router for caption, detailed caption, and object detection parsing
- Rule/mock LLM reasoning fallback for local and free execution
- Context Program and Prompt Compiler
- Prompt Rendering Engine for generation, CLIP, PickScore, and VLM Judge prompts
- Style Transfer Program, Prompt Sanitizer, and Prompt Validator for long prompt structuring
- Provider routing and provider prompt adaptation
- Generation Planner and Generation Router with fast/quality modes
- Style Transfer Preset Manager for SDXL strength, IP scale, CFG, steps, and resolution
- Reference Conditioning Package for future IP-Adapter, ControlNet, and img2img
- FLUX-oriented generation path
- Multi-metric evaluation
- Adaptive planning and retry loop
- Memory, debug report, benchmark, and report generator
- Gradio UI and FastAPI service layer

## Repository Structure

The folders remain implementation-oriented, but README explains them by responsibility:

| Responsibility | Main Folders |
| --- | --- |
| Planning | `agents/`, `tools/vlm/` |
| Context | `agents/`, `knowledge/`, `llm/` |
| Generation | `agents/`, `tools/`, `config/` |
| Evaluation | `agents/`, `evaluation/`, `tools/` |
| Infrastructure | `workflow/`, `memory/`, `api/`, `ui/`, `benchmark/`, `docs/` |

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
pip install fastapi uvicorn gradio
```

`requirements.txt` keeps the core model/runtime dependencies. FastAPI, Uvicorn, and Gradio are installed separately for service/UI execution and are also installed in the Docker image.

Run Gradio:

```bash
python main.py
```

Run FastAPI:

```bash
uvicorn api.app:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Run benchmark:

```bash
python -m benchmark.benchmark_runner
```

Run report generator:

```bash
python -m benchmark.report_generator
```

Run with Docker:

```bash
docker compose up --build
```

FastAPI: `http://127.0.0.1:8000/docs`

Gradio: `http://127.0.0.1:7860`

## Debug Report / Benchmark

Debug reports make the framework inspectable.

- `report.json`: machine-readable state snapshot
- `prompt_preview.txt`: readable prompt lifecycle and trace
- prompt rendering outputs: generation prompt, CLIP prompt, PickScore prompt, VLM Judge prompt
- provider-specific rendering outputs: prompt type, dense prompt, SDXL style prompt, word count, token count
- evaluation metrics and retry information
- incremental execution fields: executed layers, skipped layers, dirty reasons, and context cache path
- output image references

Benchmark results are saved under `benchmark/results/`. Runtime outputs and API keys should not be committed.

## Incremental Execution

v1.7 adds a lightweight Context Cache for repeated runs. The Execution Engine computes signatures for stable artifacts and skips selected work when inputs are unchanged.

Cached artifacts include:

- planner goal tree
- vision result and caption
- reference image parse
- character program
- context program
- prompt compiler outputs
- generated image path when the generation prompt is unchanged and the file still exists

Skip examples:

```text
Vision unchanged      -> Skip Vision
Reference unchanged   -> Skip Reference Parser
Context unchanged     -> Skip Context Program Builder
Prompt unchanged      -> Skip Prompt Compiler
Generation unchanged  -> Skip Generation
```

Debug reports include `executed_layers`, `skipped_layers`, and `dirty_reasons`, so cache behavior can be inspected after each run.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `HF_TOKEN` | Hugging Face access token for model/provider access. |
| `LLM_PROVIDER` | Use `rule` or `mock` for the current free/local setup. |
| `VLM_PROVIDER` | `blip` or `florence`; BLIP is the default. |
| `GENERATION_PROVIDER` | `flux_fast` or `sdxl_quality`; default is `flux_fast`. |
| `SDXL_MODEL_ID` | Optional Diffusers model id for SDXL Img2Img. Default is `stabilityai/stable-diffusion-xl-base-1.0`. |
| `ALLOW_MOCK_GENERATION` | Optional test-only `true` to create an SDXL mock image after an Img2Img failure. Default is `false`. |
| `USE_IP_ADAPTER` | Optional `true` to attempt SDXL IP-Adapter conditioning. Default is `false`. |
| `IP_ADAPTER_REPO_ID` | Optional IP-Adapter repo id. Default is `h94/IP-Adapter`. |
| `IP_ADAPTER_SUBFOLDER` | Optional IP-Adapter subfolder. Default is `sdxl_models`. |
| `IP_ADAPTER_WEIGHT_NAME` | Optional adapter weight filename. Default is `ip-adapter_sdxl.bin`. |
| `IP_ADAPTER_SCALE` | Optional IP-Adapter scale. Default is `0.75`. |
| `LORA_DIR` | Optional directory for inference-only `.safetensors` LoRA files such as `ghibli`, `anime`, `watercolor`, and `realistic`. |

VLM-only local run on PowerShell:

```powershell
$env:LLM_PROVIDER="rule"
$env:VLM_PROVIDER="blip"
python main.py

$env:VLM_PROVIDER="florence"
python main.py
```

OpenAI API keys are not required for this v1.1 VLM-only setup. Never commit `.env` files or real API keys.

## Current Limitations

- BLIP is the default VLM.
- Florence-2 is available through the Vision Router and falls back to BLIP if the model cannot be loaded.
- FLUX is the default fast generation provider path.
- SDXL Img2Img is available through `GENERATION_PROVIDER=sdxl_quality` when Diffusers dependencies, model access, and a reference image are available.
- LLM reasoning remains rule/mock fallback for this release focus.
- Some adaptive planning and evaluation logic is intentionally rule-based for stability.
- Image quality depends on external provider behavior.

## Prompt Rendering Engine

The framework does not use one prompt for every model-facing task. The Prompt Rendering Engine converts the Context Program into task-specific prompts:

| Prompt | Purpose |
| --- | --- |
| `generation_prompt` | Full visual prompt used by the generation provider. |
| `clip_prompt` | Short semantic summary for CLIP-style image-text similarity. |
| `pickscore_prompt` | Human preference-oriented prompt preserving style, quality, and composition. |
| `vlm_judge_prompt` | Longer judging instruction for future reference/generated image comparison. |

Provider-specific prompt rendering is applied at Generation Router time:

| Provider | Prompt Type | Behavior |
| --- | --- | --- |
| `flux_fast` | Dense | Uses the existing rich visual prompt. |
| `sdxl_quality` | Style | Uses only `style_program` fields and keeps the prompt under 77 tokens. Identity stays in the reference image. |

The CLIP prompt is intentionally short and removes quality-only terms such as `masterpiece`, `8k`, and `ultra detailed` so evaluation focuses on character, outfit, action, and background semantics.

## Evaluation Prompt Routing

The Evaluation Layer routes prompts by metric instead of sending the full generation prompt everywhere:

| Metric | Prompt Route |
| --- | --- |
| CLIP | `clip_prompt`, then `evaluation_prompt`, then provider/user fallback. |
| Prompt Metric | `generation_prompt` compared with `context_program`. |
| Aesthetic Metric | `pickscore_prompt`, then `generation_prompt` fallback. |
| VLM Judge | `vlm_judge_prompt` skeleton, disabled by default. |
| DINO Identity | Reference image to generated image visual consistency. |

This avoids CLIP token overflow. CLIP has a short text budget, commonly 77 tokens, so long generation prompts with quality tags and negative prompt terms are not suitable for image-text similarity scoring.

CLIP and DINO evaluate different things:

- CLIP: text-image semantic alignment.
- DINO: reference image to generated image visual identity consistency.
- Prompt Metric: generation prompt and context program consistency.
- Aesthetic Metric: lightweight heuristic for quality, composition, and prompt structure.

If any metric fails, the workflow continues. CLIP and DINO return disabled fallback results when their model, input, or image data is unavailable. Prompt and Aesthetic metrics fall back to `user_prompt` when richer prompt variants are missing.

The Evaluation Layer returns a stable `evaluation_result` schema with `metrics`, `semantic_alignment`, `identity_preservation`, `prompt_consistency`, `aesthetic_quality`, `overall_score`, `weighted_score`, `metric_summary`, and `used_fallback`. Weighted score is calculated from enabled metrics only, using default weights for CLIP, DINO, Prompt, and Aesthetic metrics.

## Roadmap

| Release | Focus |
| --- | --- |
| v1.0 RC1 | Layer-based documentation cleanup |
| v1.0 RC2 | Responsibility refactoring and framework simplification |
| v1.0 | Demo polish, CI, and deployment-ready release |
| v1.7 | Context Cache and Incremental Execution |
| v2.0 | Generation Quality Upgrade with provider-independent Generation Router |
| v2.1 | Reference Conditioning Interface |
| v2.2 | SDXL Quality Provider Integration |
| v2.3 | SDXL Style Prompt Renderer |
| v2.4 | Reference-aware Style Transfer with Style Program, LoRA hook, and ControlNet hook |

## Portfolio Highlights

- AI Agent Architecture
- Responsibility-driven framework design
- Context Engineering
- Prompt Compiler design
- Provider abstraction
- Multi-metric evaluation
- Adaptive planning
- Debuggable AI workflow
- FastAPI and Gradio integration

## Documentation

- [Architecture](docs/architecture.md)
- [Layer Map](docs/layer_map.md)
- [Project Summary](docs/project_summary.md)
- [Design Specification v1.0](docs/design_spec_v1.md)
- [Demo Guide](docs/demo_guide.md)
- [Interview Notes](docs/interview_notes.md)
- [Roadmap](docs/roadmap.md)
- [v1.0 RC2 Release Notes](docs/release_notes_v1_rc2.md)

## License

No license has been selected yet. Add a license before public distribution.
