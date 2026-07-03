# Prompt Archive 043: LLM Prompt Critic

## Objective

Add an optional LLM-style prompt critic interface after rule-based PromptCritic and before PromptOptimizer.

## Prompt Intent

The prompt asked for an architecture-focused Sprint. The key constraint was to avoid real external LLM API calls while designing an interface that can later support OpenAI or local LLMs.

## Files Allowed

- `agents/llm_prompt_critic_agent.py`
- Planner, Orchestrator, ExecutionEngine, ToolRegistry, DebugReport
- README and selected docs

## Files Forbidden

Model tools, generation/evaluation agents, retrieval/knowledge agents, prompt assembler, prompt optimizer, provider router/adapter, memory, UI, API, benchmark, main, requirements, env, and outputs.

## Result

`LLMPromptCriticAgent` returns a structured report with semantic issues, conflicts, priority issues, provider suitability issues, suggestions, priority fixes, and score.

## Future Work

Connect a real LLM backend behind the same interface and keep disabled/mock/fallback behavior.
