# Sprint 37: Benchmark Runner

## Objective

Run multiple prompts automatically and save benchmark results for comparison.

## Problem

Single-run testing does not show whether prompt and agent changes improve the system across different prompt types.

## Design Decision

Add a standalone `benchmark/` layer that calls the existing orchestration workflow and writes timestamped result JSON files.

## Implementation Summary

- Added `benchmark/prompts.json`.
- Added `benchmark/benchmark_runner.py`.
- Added `benchmark/results/`.
- Each prompt result records provider, score, best score, retry status, image path, debug report path, prompt preview path, prompt length, and agent trace.
- Individual prompt failures are captured without stopping the benchmark.

## AI Agent Concept

Benchmarking helps evaluate agent workflow behavior across repeated scenarios.

## Prompt Engineering Note

The prompt set includes basic anime style, photobooth memory collage, and soft character portrait cases to exercise different prompt orchestration paths.

## Interview Talking Points

- Benchmark Runner makes quality changes measurable.
- Debug report paths connect aggregate benchmark results to run-level observability.
- Error isolation keeps long-running tests useful even when one case fails.

## Future Work

- Benchmark dashboard
- Prompt A/B testing
- Regression thresholds
- Scheduled benchmark runs
