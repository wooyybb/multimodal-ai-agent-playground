# Layer Map

Layer-based view is used for documentation and portfolio communication. Internal implementation may still use individual agent classes.

## Planning Layer

- Role: Understand user intent and reference image.
- Includes: Vision, Goal Planning, Reference Parsing, Character Extraction, Scene Planning.
- Input: user prompt, input image, caption, vision result, previous planning state.
- Output: goal tree, reference image structure, character program, scene plan.

## Context Layer

- Role: Build generation-ready context.
- Includes: Character Program, Context Program, Prompt Compilation, Prompt Validation, Negative Prompt, Prompt Optimization, Prompt Compression.
- Input: planning output, retrieval context, memory context, provider constraints.
- Output: context program, context validation, optimized prompt, compiled prompt package.

## Generation Layer

- Role: Generate according to provider requirements.
- Includes: Provider Router, Provider Adapter, Generation Agent, FLUX.
- Input: compiled prompt package, provider config, provider prompt.
- Output: generated image path and provider generation metadata.

## Evaluation Layer

- Role: Evaluate result and adapt the next plan.
- Includes: Evaluation Aggregator, Reflection, Hypothesis, Strategy, Adaptive Planning, Retry.
- Input: generated image, reference image, prompt package, score, context program.
- Output: metrics, weighted score, reflection, adaptive plan, retry decision, best result.

## Infrastructure Layer

- Role: Support persistence, debugging, comparison, and access.
- Includes: Memory, History, Debug Report, Benchmark, Report Generator, FastAPI, Gradio.
- Input: full execution state, output paths, metrics, prompts, trace.
- Output: history record, debug report, benchmark result, API/UI access.

## Note

Layer-based view is used for documentation and portfolio communication. Internal implementation may still use individual agent classes.
