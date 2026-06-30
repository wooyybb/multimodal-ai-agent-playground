# Multi-Agent Image Generation Workflow

## Project Overview

This project is an end-to-end AI Agent Engineering demo that connects image understanding, prompt generation, image generation, evaluation, reflection, retry, and memory into one workflow.

The system started as a single multimodal pipeline and evolved into a Python class-based multi-agent architecture with a Gradio UI.

## Multi-Agent Architecture

```text
User
-> Gradio UI
-> MultimodalPipeline
-> OrchestratorAgent
-> VisionAgent / BLIP
-> PromptAgent
-> GenerationAgent / FLUX or fallback
-> EvaluationAgent / CLIP
-> ReflectionAgent
-> RetryAgent
-> MemoryManager
-> UI Output
```

Current workflow:

```text
Image -> BLIP -> PromptAgent -> FLUX -> CLIP -> Reflection -> Retry -> Memory
```

## Setup

Create and activate a Python environment, then install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a local `.env` file if you want to use real Hugging Face FLUX generation.

Use `.env.example` as a template, but do not paste real token values into documentation or committed files.

Do not commit real API tokens. If the Hugging Face token environment variable is not configured, the project uses a fallback mock image so the workflow can still run.

## Run

```bash
python main.py
```

This launches the Gradio UI. Upload an image, enter a user prompt, and run the multi-agent workflow.

## Demo Screenshots / Images

Selected demo screenshots and curated generated examples should be stored under:

```text
assets/demo/
```

Do not commit the entire `outputs/` folder. `outputs/` is runtime output storage and may contain many temporary generated files.

## Known Limitations

- First BLIP or CLIP run can take time because models may need to download.
- FLUX real generation requires a valid Hugging Face token configured locally.
- Without a local Hugging Face token environment variable, FLUX uses a fallback mock image.
- CLIP score mainly measures image-text alignment, not full visual quality.
- Fallback mock images are useful for workflow validation but not real generation quality evaluation.

## Future Work

- Add curated demo images under `assets/demo/`.
- Add history viewer UI for `memory/history.json`.
- Add reference-image similarity evaluation.
- Improve retry policy beyond one-step retry.
- Add richer generation options such as seed, size, and batch count.
- Prepare README screenshots and demo video after model/runtime stabilization.
