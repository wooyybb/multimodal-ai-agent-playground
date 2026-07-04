# Demo Guide

This guide is for interviews, portfolio demos, and quick local validation.

## 1. Run Gradio Demo

```bash
python main.py
```

Use this path when you want to show the interactive workflow:

1. Upload or provide an image.
2. Enter a user prompt.
3. Run generation.
4. Show output image and score.
5. Open debug report for trace details.

## 2. Run FastAPI Service

```bash
uvicorn api.app:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Use this path when explaining backend/service readiness.

## 3. Run Benchmark

```bash
python -m benchmark.benchmark_runner
```

Benchmark results are saved under `benchmark/results/`.

Use this path to show that the framework can run multiple prompts and compare scores, retry behavior, provider, and debug report paths.

## 4. Run Report Generator

```bash
python -m benchmark.report_generator
```

Use this path to show benchmark result summarization for review.

## 5. Run with Docker

Docker Compose starts both the FastAPI service and Gradio UI with the same project image.

```bash
docker compose up --build
```

FastAPI Swagger:

```text
http://127.0.0.1:8000/docs
```

Gradio:

```text
http://127.0.0.1:7860
```

Stop the containers:

```bash
docker compose down
```

Keep real keys in a local `.env` file only. Do not add `.env` or generated `outputs/` files to Git.

## 6. Check Debug Report

Runtime debug artifacts are saved under `outputs/runs/`.

Important files:

- `report.json`: machine-readable state snapshot
- `prompt_preview.txt`: human-readable prompt and agent trace summary
- copied output images when available

Do not commit the full `outputs/` folder.

## Interview Demo Talking Points

- This is not a prompt-to-image script; it is an inspectable agent framework.
- Context Program is a structured intermediate representation before prompt compilation.
- Prompt Compiler converts context into provider-specific prompt packages.
- Multi-Metric Evaluation is more explainable than CLIP-only scoring.
- Self Verification and Strategy Selector decide whether replanning is necessary.
- Debug Report makes the system auditable.

## Expected Questions

Q. What should I show first?
A. Show README architecture, then run Gradio, then open a debug report.

Q. What if model loading is slow?
A. Explain the architecture using debug report and benchmark outputs. The project intentionally keeps mock/fallback paths for development stability.

Q. What is the strongest engineering point?
A. The separation between context engineering, prompt compilation, provider routing, evaluation, and adaptive reasoning.
