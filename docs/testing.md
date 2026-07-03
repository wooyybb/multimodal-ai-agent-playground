# Testing

## Current Checks

- `python -m compileall agents tools workflow memory ui registry knowledge api benchmark`
- Import checks for Gradio and FastAPI entry points
- Targeted unit-style checks for new agent steps when added

## Manual Checks

- Run Gradio with `python main.py`.
- Run FastAPI with `uvicorn api.app:app --reload`.
- Run benchmark with `python -m benchmark.benchmark_runner`.
- Generate benchmark report with `python -m benchmark.report_generator`.

## Future Work

- Add automated unit tests for provider prompt adapters.
- Add Context Program schema tests.
- Add benchmark regression tests.
