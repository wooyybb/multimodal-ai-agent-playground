# Development Log

This log keeps a short summary of each sprint. Detailed notes live in `docs/sprint_book/`.

## Sprint 01-05

- Built the initial agent skeleton.
- Added VisionAgent, PromptAgent, GenerationAgent, and EvaluationAgent.
- Used mock BLIP/FLUX/CLIP behavior first to stabilize interfaces.

## Sprint 06-10

- Added ReflectionAgent and RetryAgent.
- Added MemoryManager and one-step retry loop.
- Added Gradio UI.
- Replaced mock captioning with real BLIP integration.

## Sprint 11-15

- Added FLUX generation path with fallback.
- Added CLIP evaluation path.
- Documented integration validation.
- Added PlannerAgent and early planning structure.

## Sprint 16-20

- Added ToolRegistry.
- Introduced Context Engineering and prompt compression.
- Added DynamicExecutionEngine.
- Added KnowledgeManager and RetrievalAgent.

## Sprint 21-25

- Added semantic-like memory retrieval.
- Built multi-agent prompt orchestration.
- Added character reference handling.
- Upgraded LayoutAgent and ScenePlanningAgent.

## Sprint 26-30A

- Added ProviderPromptAdapter.
- Added ProviderRouter and config-driven provider capability setup.
- Added PromptCriticAgent.
- Standardized selected agents around `run(state) -> dict`.

## Sprint 31-35

- Added PromptOptimizerAgent.
- Added Intelligent Prompt Optimizer behavior.
- Added LLMPromptOptimizer interface.
- Added AgentState.
- Added FastAPI service layer.

## Sprint 36-39

- Added DebugReportManager and prompt preview files.
- Added Benchmark Runner.
- Added Run Comparison Report generator.
- Added ContextProgramBuilder and provider-independent context program.

## Sprint 39.5

- Refactored documentation into README-first project docs.
- Reduced duplicated explanations across core docs.
- Updated roadmap, architecture, concepts, interview notes, and prompt engineering docs.

## Sprint 40

- Added `ContextProgramValidator`.
- Inserted validation between `ContextProgramBuilder` and `PromptAssembler`.
- Validation records missing keys, type warnings, provider warnings, suggestions, and score.
- Debug reports now include `context_validation`.

## Sprint 41

- Added `LLMContextReasoner`.
- Added a mock LLM interface for semantic planning without external API calls.
- Reasoner outputs user goal, scene goal, composition goal, interaction goal, style goal, and priority list.
- Debug reports now include `context_reasoning`.

## Sprint 43

- Added `LLMPromptCriticAgent`.
- Inserted LLM prompt critique after rule-based `PromptCriticAgent` and before `PromptOptimizerAgent`.
- Added disabled, mock, and future llm fallback modes without external API calls.
- Debug reports now include `llm_prompt_critic_report` and `llm_prompt_critic_score`.

## Sprint 44

- Added shared `llm/` provider abstraction layer.
- Added `BaseLLM`, `LLMClient`, `MockLLM`, and `LLMProviderRegistry`.
- Refactored LLMContextReasoner, LLMPromptCriticAgent, and LLMPromptOptimizerAgent to call LLMClient.
- Kept external LLM API calls disabled; only MockLLM is implemented.

## Sprint 45

- Added `PromptCompiler`.
- Inserted `prompt_compiler` after `provider_router` and before `provider_prompt_adapter`.
- Added `compiled_prompt_package` with positive prompt, negative prompt, prompt blocks, compiler notes, and prompt budget.
- ProviderPromptAdapter now uses compiled prompt packages when available.

## Sprint 46

- Added `AIModelService`.
- Added provider skeletons for mock, OpenAI, Gemini, Claude, and Ollama.
- Updated `LLMClient` to call AIModelService instead of providers directly.
- Kept all external API calls disabled.

## Sprint 47

- Implemented optional real OpenAIProvider integration.
- Added `OPENAI_API_KEY`, `OPENAI_MODEL`, and `LLM_PROVIDER=openai` support.
- Added no-key, client-error, request-error, and JSON-parse fallback behavior.
- Preserved agent isolation: agents still call `LLMClient`, not OpenAI directly.

## Sprint 48

- Added `tools/vlm/` as a VLM Adapter Layer.
- Refactored `VisionAgent` to use `VLMRouter` instead of depending directly on `BlipTool`.
- Added BLIPVLM as the default provider plus Florence-2 and Qwen-VL skeleton providers.
- Debug reports now include structured `vision_result` metadata when available.

## Sprint 49

- Added `AdaptivePlanner` after `ReflectionAgent` and before `RetryAgent`.
- Added rule-based failure analysis, hypothesis generation, strategy, context updates, priority changes, and confidence.
- Retry now applies adaptive context updates and re-runs prompt compiler/provider adapter before the second generation attempt.
- Debug reports now include `adaptive_plan`.

## Sprint 50

- Added `CharacterProgramBuilder`.
- Converted BLIP caption and vision result into structured character identity, appearance, style, pose, expression, colors, and identity rules.
- ExecutionEngine now runs CharacterProgramBuilder after VisionAgent.
- Context Program and PromptCompiler receive Character Program data through execution-engine context injection.
- Debug reports now include `character_program`.

## Sprint 51

- Added `GoalPlanner`.
- Planner now creates a Goal Tree with main goal, sub-goals, priority weights, and success criteria.
- ExecutionEngine stores Goal Tree and injects goal priorities into Context Program before prompt compilation.
- Debug reports now include `goal_tree`.

## Sprint 53

- Added `StrategySelector`.
- StrategySelector generates candidate strategies and selects the highest-scoring option.
- AdaptivePlanner now reads `selected_strategy` when building the adaptive plan.
- ExecutionEngine injects selected strategy into Context Program before prompt compilation.
- Debug reports now include `candidate_strategies` and `selected_strategy`.

## Sprint 54

- Added `SelfVerificationAgent`.
- Self Verification checks goal satisfaction, prompt consistency, context consistency, and replanning need.
- Planner and ExecutionEngine now run self verification between reflection and strategy selection.
- StrategySelector references self verification to select low-risk or issue-focused strategies.
- Debug reports now include `self_verification`.

## Sprint 55

- Added `evaluation/` metric layer.
- Added CLIP, Identity, Prompt, and Aesthetic metric classes.
- Added `EvaluationAggregator` with weighted scoring.
- Refactored `EvaluationAgent` to use the aggregator while preserving float score compatibility.
- Debug reports now include metrics, weighted score, and metric summary.

## Future Work

- Keep this file short.
- Move deep sprint details to `docs/sprint_book/`.
- Keep architecture changes reflected in README and `docs/architecture.md`.
