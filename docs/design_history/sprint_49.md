# Sprint 49 Design History

## Problem

RetryAgent only used score threshold, so a failed generation could be retried without a clear strategy.

## Decision

Add `AdaptivePlanner` between Reflection and Retry.

## Reason

The framework needs re-planning, not only regeneration. Reflection should produce actionable context updates before the next prompt compilation.

## Future

Add LLM-assisted adaptive planning and benchmark adaptive retry improvements.
