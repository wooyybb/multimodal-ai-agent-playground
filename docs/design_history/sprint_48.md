# Sprint 48 Design History

## Problem

VisionAgent depended directly on BLIP, so replacing or comparing vision-language models would require changing agent code.

## Decision

Introduce a VLM Adapter Layer with `VLMRouter`, `BLIPVLM`, `FlorenceVLM`, and `QwenVLM`.

## Reason

BLIP remains the stable default, while Florence-2 and Qwen-VL can be added later behind the same `analyze()` interface.

## Future

Add real Florence/Qwen providers and expand `vision_result` with objects, style hints, character hints, and reference-image understanding.
