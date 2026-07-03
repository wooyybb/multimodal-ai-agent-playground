# Sprint 48 Prompt Archive

## Task

Add a Multi-VLM Adapter so VisionAgent no longer depends directly on BLIP.

## Architecture Prompt

The prompt specified a current structure of `VisionAgent -> BlipTool -> caption` and a target structure of `VisionAgent -> VLMRouter -> BLIPVLM / FlorenceVLM / QwenVLM -> vision_result`.

## Files Allowed

New files under `tools/vlm/`, plus scoped updates to VisionAgent, BlipTool, debug report, README, and selected docs.

## Files Forbidden

Generation, evaluation, reflection, retry, provider adapter, LLM, memory, knowledge, UI, API, benchmark, main, requirements, env, and outputs were kept out of scope.

## Done Definition

The sprint is complete when BLIP remains the default, skeleton VLM providers exist, `vision_result` is available for debug reporting, and existing BLIP/FLUX/CLIP workflow compatibility is preserved.
