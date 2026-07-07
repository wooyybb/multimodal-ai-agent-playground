# Development Log

This log keeps a short summary of each sprint. Detailed notes live in `docs/sprint_book/`.

## Version 3.1

- Refactored architecture explanation into five top-level agents: Understanding, Planning, Generation, Evaluation, and Reflection.
- Added ToolRegistry agent-group metadata and ExecutionEngine component trace fields.
- Updated README, architecture, project summary, interview notes, and release notes around Agent vs Module terminology.

## Version 3.2

- Added the `modules/` package and grouped lower-level implementations by Understanding, Planning, Generation, Evaluation, Reflection, Prompt, and Memory responsibilities.
- Kept `agents/` compatibility wrappers so existing imports and execution plans continue to work.
- Updated Registry and Orchestrator imports to use implementation modules directly where practical.

## Version 3.3

- Compressed `agents/` to the five high-level agent files plus `orchestrator_agent.py`.
- Removed small compatibility wrappers after moving runtime imports to `modules.*`.
- Added `core/` façades for style transfer program, semantic prompt engine, reference conditioning, generation routing, evaluation runner, and debug report.

## Version 3.4

- Added Provider Prompt Compiler V2 for model-specific prompt compilation.
- Split prompt policy into FLUX dense, SDXL Img2Img style, CLIP evaluation, and negative prompt outputs.
- Added token budget optimization and debug reporting for removed weak/internal prompt phrases.

## Pre-v4.0 Architecture Cleanup

- Re-aligned README and architecture docs around the five high-level agents.
- Marked Requirement Parser as a future Planning Agent module slot without adding LLM API calls.
- Kept existing generation, evaluation, SDXL Img2Img, IP-Adapter, and ControlNet flows unchanged.

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

## Version 1.5

- Upgraded Florence-2 from caption-only use to a Vision Parser path.
- Florence now runs `<CAPTION>`, `<DETAILED_CAPTION>`, and `<OD>` sequentially.
- Standard vision results now include structured `objects`, `regions`, and `ocr` skeleton fields.
- `ReferenceImageParser` prioritizes object detection results before detailed captions and caption fallback.

## Version 1.6

- Stabilized Evaluation Result and Metric Result schemas.
- Weighted score now uses enabled metrics only.
- CLIP/DINO failures return disabled fallback metric results instead of crashing the workflow.
- Debug report preview now shows a human-readable Evaluation Result block with metric status and reasons.

## Version 1.7

- Added Context Cache support under `memory/context_cache.json`.
- ExecutionEngine now performs dirty checks before selected planning, context, compiler, and generation steps.
- Unchanged artifacts can be restored from cache and marked as skipped.
- Debug reports now include executed layers, skipped layers, dirty reasons, and context cache path.

## Version 2.0

- Added provider-independent Generation Planner and Generation Router.
- Preserved the existing FLUX path as `flux_fast` Fast Mode.
- Added `sdxl_quality` as a skeleton Quality Mode provider with CFG, steps, scheduler, and resolution metadata.
- Debug reports now store generation provider, mode, preset, and future hooks for IP Adapter and ControlNet.

## Version 2.1

- Added Reference Conditioning Package schema.
- PromptCompiler now creates `reference_conditioning_package` from context, reference image, and character program.
- ProviderPromptAdapter preserves the package and records prompt-only fallback notes when conditioning is unsupported.
- Debug reports now show reference conditioning status, strengths, preserve flags, and notes.

## Version 2.2

- Added `GenerationConfig` and `GenerationResult` for provider-independent generation output.
- GenerationRouter now supports `GENERATION_PROVIDER=flux_fast` and `GENERATION_PROVIDER=sdxl_quality`.
- SDXL Quality Provider can optionally attempt `diffusers` execution, with mock fallback as the default safe path.
- Debug reports now include generation config, prompt length, provider, mode, CFG, steps, scheduler, resolution, and latency.

## Version 2.3

- Added optional IP-Adapter hook inside SDXL Quality Provider.
- SDXL provider now reads `reference_conditioning_package` and records conditioning status.
- `USE_IP_ADAPTER=false` keeps prompt-only generation by default.
- Missing adapter files or hook failures fall back gracefully and record the reason in debug reports.

## Version 2.4

- Added Style Program generation for reference-aware style transfer.
- Added inference-only LoRA loader hook for `.safetensors` files.
- Added ControlNet placeholder hook for OpenPose, Depth, and Canny.
- SDXL provider now records style program, selected LoRA, IP-Adapter, and ControlNet status in debug output.

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
- Stabilized the v1.1 scope as VLM-only: `VLM_PROVIDER=blip` or `VLM_PROVIDER=florence`, with LLM reasoning kept on rule/mock fallback.
- CharacterProgramBuilder now prioritizes `reference_image` when building character identity, appearance, style, and dominant colors.
- Debug reports expose VLM provider, fallback status, latency, `reference_image`, and `character_program`.

## Version 1.2

- Deferred paid LLM API focus.
- Keep default reasoning on rule/mock fallback while stabilizing the Vision Layer first.
- Future work can revisit real LLM reasoning after the VLM/reference image pipeline is stable.
- Added Prompt Rendering Engine behavior to PromptCompiler.
- PromptCompiler now renders `generation_prompt`, `clip_prompt`, `pickscore_prompt`, `vlm_judge_prompt`, and `negative_prompt`.
- ExecutionEngine uses `generation_prompt` for generation and `clip_prompt` for CLIP-style evaluation.
- Debug reports now store prompt rendering outputs in both `report.json` and `prompt_preview.txt`.

## Version 1.3

- Added Evaluation Prompt Routing.
- CLIP Metric now prioritizes `clip_prompt` and records the prompt type used.
- Prompt Metric compares `generation_prompt` with `context_program`.
- Aesthetic Metric prioritizes `pickscore_prompt`.
- Added disabled skeleton metric results for VLM Judge and DINO identity without loading new models.
- Evaluation result now includes semantic alignment, identity preservation, prompt consistency, aesthetic quality, overall score, weighted score, metric summary, and routing info.

## Version 1.4

- Added DINO Identity Metric for reference image to generated image visual consistency.
- DINO uses `facebook/dinov2-small` through `torch` and `transformers` when available.
- If reference/generated image or model loading is unavailable, DINO returns `enabled=false` without crashing.
- Evaluation weighting now uses CLIP 0.40, DINO 0.25, Prompt 0.20, Aesthetic 0.15 when DINO is enabled.
- If DINO is disabled, identity preservation falls back to the existing rule-based identity metric.

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

## Version 2.5

- Added Style Transfer Program generation for long reference-aware style transfer prompts.
- Added Prompt Sanitizer to remove forbidden concepts, merge semantic duplicates, deduplicate phrases, and enforce provider token budgets.
- Added Prompt Validator to check forbidden concept survival, duplicate count, SDXL/CLIP token limits, and style/layout preservation.
- Debug reports now include `style_transfer_program`, `forbidden_concepts`, `prompt_sanitizer_report`, `prompt_validation_report`, and `sdxl_style_prompt`.

## Version 2.6

- Added `StylePresetManager` and `GenerationPreset`.
- SDXL quality generation now selects `subtle_transfer`, `balanced_transfer`, `strong_style_transfer`, `photobooth_soft`, `ugly_cute_drawing`, `anime_webtoon`, or `realistic_preserve` from `style_transfer_program`.
- Generation preset values drive SDXL `strength`, IP-Adapter scale, CFG, steps, and resolution.
- Environment overrides are supported through `SDXL_STRENGTH`, `IP_ADAPTER_SCALE`, `SDXL_CFG`, `SDXL_STEPS`, `SDXL_WIDTH`, and `SDXL_HEIGHT`.
- Debug reports now include `generation_preset`, `preset_reason`, and `environment_overrides`.

## Version 2.7

- Added Semantic Prompt Program to manage prompt intent as sections instead of one growing string.
- Added Semantic Merge for meaning-level duplicate reduction.
- Added Conflict Resolver so user forbidden intent overrides caption or agent-added concepts.
- Added Provider Renderer for FLUX dense prompt, SDXL style prompt, and CLIP evaluation prompt views.
- Prompt Preview now includes section-based Identity, Style, Layout, Scene, Lighting, Quality, Negative, and Constraints blocks.

## Version 2.8

- Added Reference Analyzer for width, height, aspect ratio, character ratio, background ratio, face ratio, focus, and quality estimation.
- Added Reference Preprocessor with aspect-ratio-preserving resize, auto center crop, auto padding, and longest-edge resize behavior.
- SDXL Img2Img and IP-Adapter now receive the conditioned reference image instead of relying on raw reference dimensions.
- Debug reports now include `reference_analysis`, `conditioning_summary`, and `conditioned_reference_path`.

## Version 2.9

- Added optional ControlNet hook for SDXL Img2Img.
- Implemented Canny control image generation from the conditioned reference image.
- Depth and OpenPose remain planned hook types.
- SDXL provider attempts ControlNet pipeline loading only when `USE_CONTROLNET=true`.
- If ControlNet loading fails, the workflow falls back to existing SDXL Img2Img + IP-Adapter.
- Debug reports now include ControlNet enabled/loaded/type/scale/control image/fallback fields.

## Version 3.0

- Added `LLMStyleTransferPlanner`.
- LLM reasoning now creates a JSON Style Transfer Program instead of directly writing final prompts.
- `LLM_PROVIDER=rule` keeps the existing rule-based fallback behavior.
- `LLM_PROVIDER=openai` attempts structured planning and falls back without crashing when API key/client/JSON parsing fails.
- PromptCompiler now sends the final Style Transfer Program into the Semantic Prompt Engine for provider-specific rendering.
- Debug reports include LLM planner output, fallback status, reasoning summary, final Style Transfer Program, and generation strategy.

## Future Work

- Keep this file short.
- Move deep sprint details to `docs/sprint_book/`.
- Keep architecture changes reflected in README and `docs/architecture.md`.
