# Refactoring Notes v4.0

## What Changed

v4.0 adds an LLM Requirement Parser inside the Planning Agent boundary. The parser converts a long user requirement into structured Style Transfer Program JSON.

It does not write the final prompt.

## Why LLM Is a Requirement Parser, Not a Prompt Writer

Final prompts are provider-specific. FLUX, SDXL Img2Img, CLIP evaluation, and negative prompts need different text views and token budgets. If the LLM writes the final prompt directly, the framework loses control over forbidden concepts, reference conditioning, and provider-specific rendering.

The LLM therefore parses requirements into structured fields. The framework still renders final prompts through the Semantic Prompt Engine and Provider Prompt Compiler.

## Style Transfer Program Benefits

The Style Transfer Program keeps intent explicit:

- task goal
- identity preservation policy
- style direction
- layout and panel rules
- pose and expression constraints
- text rules
- negative/remove concepts
- generation strategy

This makes the workflow debuggable and provider-independent.

## Rule Fallback

`LLM_PROVIDER=rule` uses deterministic parsing. `LLM_PROVIDER=openai` attempts OpenAI JSON parsing. If `OPENAI_API_KEY` is missing, the OpenAI client is unavailable, the request fails, or JSON parsing fails, the parser returns the rule-based Style Transfer Program.

The workflow does not crash.

## Relationship to Provider Prompt Compiler

The parser output is not sent directly to the image model. It is passed into the existing context and semantic prompt path:

```text
Style Transfer Program
  |
  v
Semantic Prompt Engine
  |
  v
Provider Prompt Compiler
  |
  +-- FLUX dense prompt
  +-- SDXL Img2Img style prompt
  +-- CLIP evaluation prompt
  +-- negative prompt
```

## Reference-aware Style Transfer Alignment

The parser keeps identity and reference preservation as structured policy instead of burying it in a prompt string. This matches the project goal: reference-aware style transfer using SDXL Img2Img, optional IP-Adapter, optional ControlNet, evaluation, and adaptive planning.

## Future Video / 3D Extension

Because the LLM produces a structured program instead of a final prompt, the same requirement parsing approach can later target video, 3D, or multi-frame generation providers. New renderers can consume the same structured intent and produce provider-specific instructions.

## Engineering Review

1. The LLM is used as a Requirement Parser because structured intent is easier to validate, render, debug, and fallback than raw prompt text.
2. Style Transfer Program gives the framework a provider-independent planning representation.
3. Rule fallback keeps local/default execution stable and prevents OpenAI failures from crashing the workflow.
4. Provider Prompt Compiler remains the only owner of final model-facing prompt text.
5. The design stays aligned with reference-aware style transfer because identity, style, layout, and generation strategy are explicit fields.
6. Video/3D extension can reuse the parser output and add new provider renderers later.
