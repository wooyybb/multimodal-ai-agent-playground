# Sprint 36: Prompt Debug Report & Trace Viewer

## Objective

Save run-level debug reports that capture prompt lifecycle, intermediate agent outputs, scores, retry results, and trace logs.

## Problem

The final generated image alone does not explain which agent decision or prompt transformation produced the result.

## Design Decision

Add `DebugReportManager` and store each run under `outputs/runs/run_YYYYMMDD_HHMMSS/`.

## Implementation Summary

- Added `workflow/debug_report.py`.
- Integrated debug artifact saving before memory save.
- Saved `report.json` and `prompt_preview.txt`.
- Copied initial, retry, and best images when source files exist.
- Stored debug paths in memory history.

## AI Agent Concept

This Sprint introduces Observability, Trace Logging, Prompt Lifecycle Tracking, and Reproducible Generation Workflow.

## Prompt Engineering Note

Prompt debugging requires comparing canonical prompt, optimized prompt, provider prompt, evaluation prompt, and retry prompt in one place.

## Interview Talking Points

- Debug report explains why a generation result happened.
- prompt_preview.txt is human-readable.
- report.json is machine-readable.
- Debug saving is best-effort so it does not break workflow.

## Future Work

- UI Trace Viewer
- Benchmark Runner
- Run comparison dashboard
