# Sprint29 Design History

## Problem

The prompt moved directly from PromptAssembler to provider routing and generation. Prompt defects were only discovered after image generation.

## Decision

Add `PromptCriticAgent` before ProviderRouter.

## Reason

Prompt critique is cheaper and easier before generation. It makes duplicate keywords, missing sections, and prompt length issues visible in a structured report.

## Alternatives

- Put critique logic inside PromptAssembler.
- Wait until EvaluationAgent scores the generated image.
- Use an LLM critic immediately.

## Chosen Approach

Start with a rule-based `PromptCriticAgent` so the architecture is testable without new model dependencies.

## Future

- LLM Critic
- Semantic Critic
- Provider-specific Critic
