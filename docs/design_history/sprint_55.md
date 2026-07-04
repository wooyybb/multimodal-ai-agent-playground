# Sprint 55 Design History

## Problem

CLIP similarity alone cannot explain identity preservation, prompt completeness, or aesthetic quality.

## Decision

Add a metric-based Evaluation Aggregator.

## Reason

Evaluation should be modular and explainable. A weighted metric layer makes future PickScore, DINO, Aesthetic Score, and VLM Judge integrations easier.

## Future

Add real PickScore, DINO similarity, learned aesthetic score, and VLM judge metrics.
