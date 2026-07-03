# Sprint 38: Run Comparison Report

## Objective

Generate Markdown and HTML reports from benchmark result JSON files.

## Problem

Benchmark results were saved as JSON, but they were not easy to compare manually.

## Design Decision

Add a file-based report generator that loads the latest benchmark result and writes Markdown and static HTML reports.

## Implementation Summary

- Added `benchmark/report_generator.py`.
- Added `benchmark/reports/`.
- Markdown report includes summary, results table, best run, failed runs, and notes.
- HTML report includes summary cards, table, best run highlight, and links/paths.

## AI Agent Concept

Run comparison improves experiment tracking and makes prompt/agent changes easier to evaluate.

## Prompt Engineering Note

The report connects score metrics with debug report paths so low-scoring runs can be inspected through prompt lifecycle artifacts.

## Interview Talking Points

- Benchmark report is for comparing many runs.
- Debug report is for inspecting one run.
- CLIP score should be interpreted carefully.

## Future Work

- Interactive dashboard
- Run comparison UI
- Score trend visualization
- Prompt A/B testing
