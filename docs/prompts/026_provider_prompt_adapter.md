# Prompt Archive 026: Provider Prompt Adapter

## Purpose

이번 prompt는 canonical prompt를 provider-specific prompt로 변환하는 adapter layer를 추가하기 위한 architecture prompt다.

## Summary

`PromptAssembler`는 provider-neutral canonical prompt를 만들고, `ProviderPromptAdapter`는 FLUX/GPT Image/SDXL에 맞는 provider prompt로 변환한다.

## Prompt Engineering Note

FLUX prompt에서는 internal planning/debug terms를 제거하고 visual subject, style, layout, pose, expression, composition 중심으로 유지한다.
