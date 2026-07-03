# Sprint 38: Run Comparison Report

## Problem

Benchmark results were stored as JSON, but they were hard to compare visually.

## Decision

Add a Markdown and HTML run comparison report generator.

## Alternatives

- Build a dashboard immediately.
- Keep JSON only.
- Manually summarize results in README.
- Use an external experiment tracking tool.

## Reason

At the MVP stage, file-based reports are simple, portable, and easy to share in GitHub or interviews.

## Future Work

- Interactive dashboard
- Run comparison UI
- Score trend visualization
- Prompt A/B testing
