# Prompt Archive 018: Prompt Compression

## Purpose

이번 prompt는 Sprint 18의 architecture prompt다. 단순 기능 구현보다 Context Engineering, Prompt Compression, Context Budget 관리를 학습하고 설계에 반영하는 것이 목적이었다.

## Structure

- Task: Prompt Compression & Context Budget Management
- Architecture: Planner -> Context Builder -> PromptCompressor -> PromptAgent
- Workspace: project3 내부만 작업
- Files Allowed: PromptCompressor, PromptAgent, OrchestratorAgent, registry, docs
- Files Forbidden: tools, workflow, memory, ui, main, README, requirements, outputs
- Requirements: raw context 금지, compressed_context만 사용, 40~60 words 유지
- Documentation: design decisions, concepts, interview notes, sprint book 업데이트
- Done Definition: compileall 성공, prompt 길이 감소, CLIP 77 token 문제 완화

## Prompt Engineering Note

이 prompt는 구현 범위와 금지 파일을 명확히 분리해 Codex가 기존 agent 구조를 흔들지 않고 PromptAgent 주변만 개선하도록 유도했다.
