# Prompt Archive 039: Context Program Builder

## Task

ContextProgramBuilder를 추가해 specialist agent output을 provider-independent structured context program으로 변환한다.

## Architecture Prompt

이번 Prompt는 코드 구현보다 architecture boundary를 명확히 하는 데 집중했다.

```text
Specialist Agents
-> ContextProgramBuilder
-> PromptAssembler
-> ProviderPromptAdapter
-> GenerationAgent
```

## Files Allowed

- `agents/context_program_builder.py`
- `agents/planner_agent.py`
- `agents/orchestrator_agent.py`
- `workflow/execution_engine.py`
- `registry/tool_registry.py`
- `agents/prompt_assembler.py`
- `agents/provider_prompt_adapter.py`
- `workflow/debug_report.py`
- `README.md`
- `docs/*`

## Files Forbidden

Model tools, memory, knowledge, UI, API, main entrypoint, requirements, environment files, and runtime outputs were not modified.

## Design Intent

Context Program은 generation prompt가 아닙니다. Prompt를 만들기 위한 structured source of truth입니다. ProviderPromptAdapter는 이 object에서 provider에 필요한 visual instruction만 추출합니다.

## Done Definition

- `context_program_builder` step added to execution plan
- Context Program returned in state
- PromptAssembler references Context Program
- ProviderPromptAdapter compiles provider prompts from Context Program
- Debug Report stores Context Program
- compileall passes
