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

## Sprint 56

- Refactored README into a GitHub landing page for portfolio review.
- Added release-oriented project summary and demo guide.
- Updated architecture, roadmap, and interview notes to match the v1.0 framework direction.
- No code functionality was changed in this sprint.

## Sprint 57

- Added Dockerfile, docker-compose.yml, and .dockerignore.
- Documented Docker Compose execution for FastAPI and Gradio.
- Kept core AI Agent code unchanged.

## Sprint 58

- Added `ReferenceImageParser`.
- Inserted reference image parsing after VisionAgent and before CharacterProgramBuilder.
- Reference Image Parser extracts identity, appearance, style, composition, colors, and identity rules from caption and vision result.
- ExecutionEngine merges reference image structure into Character Program without changing generation/evaluation code.
- Debug reports now include `reference_image`.

## Sprint 59

- Strengthened the standard VLM output schema.
- BLIPVLM now fills character_hints, style_hints, composition_hints, and color_hints using rule-based parsing.
- FlorenceVLM and QwenVLM remain skeleton adapters but return the same schema through BLIP fallback.
- ReferenceImageParser now prioritizes VLM hints before falling back to caption parsing.
- Debug reports show detailed VLM fields including provider, fallback status, composition hints, and color hints.

## Sprint 60

- Added a common Reasoning Layer with `BaseReasoner`, `OpenAIReasoner`, `ReasonerRouter`, and `JSONParser`.
- Default reasoning remains rule-based.
- `LLM_PROVIDER=openai` enables optional OpenAI JSON reasoning when an API key and client are available.
- PromptCritic, PromptOptimizer, LLMContextReasoner, StrategySelector, and HypothesisGenerator can use structured reasoning with automatic fallback.
- Debug reports can include strategy and hypothesis reasoning metadata.

## Version 1.1

- Upgraded the Vision Layer from BLIP-only captioning to provider-independent VLM routing.
- Added a Florence2 adapter that attempts HuggingFace Transformers loading and falls back to BLIP when unavailable.
- Standardized `vision_result` around `caption`, `detailed_caption`, `objects`, `characters`, `scene`, `style`, `colors`, `composition`, `provider`, `used_fallback`, and `latency`.
- Updated ReferenceImageParser to prioritize structured fields before caption fallback.
- Debug reports now preserve provider, latency, and detailed vision fields.

## Version 1.2

- Connected optional OpenAI reasoning through the existing LLM Layer instead of direct agent calls.
- Kept rule/mock fallback as the default and as the failure path for missing API keys, request errors, or invalid JSON.
- Added LLM metadata for provider, fallback status, raw text on parse failure, parse success, and latency.
- Updated LLM Prompt Critic and LLM Prompt Optimizer so `LLM_PROVIDER=openai` enables real provider attempts.
- Debug reports now surface LLM provider, fallback, raw response text, context reasoning, critic report, and optimizer report.

## Release Candidate 1

- Reorganized project communication around six layers: Planning, Context, Generation, Evaluation, Reasoning, and Memory / Observability.
- Updated README and architecture docs as layer-based portfolio documentation.
- Added Layer Map and v1.0 RC1 release notes.
- Preserved core workflow and avoided new model, agent, tool, API, or metric functionality.

## Release Candidate 2

- Simplified public architecture into five responsibility layers: Planning, Context, Generation, Evaluation, and Infrastructure.
- Treated hypothesis, strategy, retry, reflection, and adaptive planning as internal Evaluation Layer processes.
- Updated README, architecture, project summary, demo guide, roadmap, and interview notes.
- Added v1.0 RC2 release notes.
- Added layer-readable ExecutionEngine logs and ToolRegistry metadata without changing core behavior.

## Future Work

- Keep this file short.
- Move deep sprint details to `docs/sprint_book/`.
- Keep architecture changes reflected in README and `docs/architecture.md`.
