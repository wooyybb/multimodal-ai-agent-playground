# Sprint 36: Prompt Debug Report & Trace Viewer

## Problem

As more agents were added, it became hard to trace how a final image was produced from intermediate plans, prompt edits, provider adaptation, evaluation, and retry.

## Decision

Add `DebugReportManager` to save `report.json`, `prompt_preview.txt`, and copied initial/retry/best images for each generation run.

## Alternatives

- Store everything in `memory/history.json`.
- Use console logs only.
- Show trace only in UI.
- Move to Docker before adding observability.

## Reason

Framework quality improves faster when each run is inspectable. Prompt lifecycle artifacts make debugging and interview demonstration easier.

## Future Work

- UI Trace Viewer
- Benchmark dashboard
- Run comparison
- Prompt A/B testing
- Observability API
