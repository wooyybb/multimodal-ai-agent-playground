# Sprint 48 Multi-VLM Adapter

## Objective

Decouple VisionAgent from direct BLIP usage by adding a provider-style VLM Adapter Layer.

## Background

The project started with BLIP captioning because it was the fastest way to turn an input image into text context. As the framework evolved, image understanding needed to become replaceable and richer than a single caption.

## Problem

Direct BLIP coupling makes Florence-2, Qwen-VL, or future VLM integration harder. It also limits debug reports to caption-level information.

## Design Decision

Add `BaseVLM`, `BLIPVLM`, `FlorenceVLM`, `QwenVLM`, and `VLMRouter`. BLIP is the default provider, while Florence and Qwen are skeleton fallback providers.

## Architecture

```text
VisionAgent
-> VLMRouter
-> BLIPVLM / FlorenceVLM / QwenVLM
-> vision_result
```

## Implementation Summary

- `VisionAgent` now uses `VLMRouter`.
- `BLIPVLM` wraps the existing `BlipTool`.
- Florence and Qwen providers return fallback structured results.
- Debug reports include `vision_result` when available.

## AI Agent Concept

This sprint applies provider abstraction to the visual understanding layer, similar to how LLM and generation providers are separated elsewhere in the framework.

## Prompt Engineering Note

The sprint prompt emphasized architecture, allowed files, forbidden files, provider interface, fallback behavior, and documentation.

## Codex Usage

Codex was used to implement the adapter layer, preserve workflow compatibility, and update project documentation.

## Debugging Experience

The main risk was preserving the existing caption-based downstream workflow while adding structured vision metadata.

## Interview Talking Points

- BLIP is a default provider, not the framework boundary.
- VLM Adapter enables model replaceability.
- `vision_result` is structured context; `caption` is compatibility text.

## Lessons Learned

Model-specific wrappers should be hidden behind stable interfaces before adding more providers.

## Future Work

Add real Florence/Qwen integrations and richer visual parsing for objects, characters, style, and reference-image understanding.
