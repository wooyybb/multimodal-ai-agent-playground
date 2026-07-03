# Sprint 50 Design History

## Problem

Caption-only vision output is not enough for style transfer or character preservation.

## Decision

Add `CharacterProgramBuilder` after VisionAgent.

## Reason

Character identity should be represented as structured context before prompt compilation. This keeps character preservation separate from provider-specific prompt text.

## Future

Replace rule-based parsing with richer VLM parsing and add multi-character identity tracking.
