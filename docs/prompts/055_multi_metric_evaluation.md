# Sprint 55 Prompt Archive

## Task

Refactor EvaluationAgent to use a Multi-Metric Evaluation Layer.

## Architecture Prompt

The target flow is `Generation -> Evaluation Aggregator -> CLIP / Prompt Alignment / Identity / Aesthetic Metrics -> Weighted Score -> Reflection`.

## Files Allowed

New `evaluation/` metric files, `agents/evaluation_agent.py`, debug report, README, and docs.

## Done Definition

EvaluationAggregator runs, CLIP metric remains, rule metrics are added, weighted score is produced, Reflection receives the weighted score, and debug report stores metric details.
