# Prompt Archive 027: Provider Router

## Purpose

이번 prompt는 provider 선택 책임을 ProviderPromptAdapter에서 분리해 ProviderRouter로 독립시키기 위한 architecture prompt다.

## Summary

ProviderRouter는 user prompt와 scene plan을 기반으로 requested provider를 추론하고, 현재 available provider가 아니면 FLUX로 fallback한다.

## Prompt Engineering Note

Provider별 prompt 최적화와 provider selection은 서로 다른 책임이므로 분리했다.
