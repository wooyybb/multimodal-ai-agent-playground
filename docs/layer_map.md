# Layer Map

Layer-based view is used for documentation and portfolio communication. Internal implementation may still use individual agent classes.

## Planning Layer

- Role: Interpret user intent, reference image, goal, scene, and character identity.
- Included agents: PlannerAgent, GoalPlanner, ScenePlanningAgent, ReferenceImageParser, CharacterProgramBuilder.
- Input: user prompt, image, caption, vision result, previous planning state.
- Output: execution plan, goal tree, reference image structure, scene plan, character program.

## Context Layer

- Role: Convert planning results into provider-independent Context Program and prompt program.
- Included agents: ContextProgramBuilder, ContextProgramValidator, PromptAssembler, PromptCompiler, PromptCompressor, NegativePromptAgent.
- Input: planning outputs, retrieval context, memory context, provider constraints.
- Output: context program, context validation, canonical prompt, compiled prompt package.

## Generation Layer

- Role: Select provider, adapt prompt, and run image generation.
- Included agents/tools: ProviderRouter, ProviderPromptAdapter, GenerationAgent, FLUX Tool.
- Input: compiled prompt package, provider config, provider prompt.
- Output: generated image path and provider-specific generation metadata.

## Evaluation Layer

- Role: Evaluate generated output with multiple metrics.
- Included agents/metrics: EvaluationAgent, EvaluationAggregator, CLIP Metric, Identity Metric, Prompt Metric, Aesthetic Metric.
- Input: reference image, generated image path, prompt, character program, compiled prompt package.
- Output: metrics, weighted score, metric summary.

## Reasoning Layer

- Role: Analyze evaluation results, generate hypotheses, select strategy, verify goals, and adapt plan.
- Included agents: ReflectionAgent, LLMContextReasoner, LLMPromptCriticAgent, LLMPromptOptimizerAgent, HypothesisGenerator, StrategySelector, SelfVerificationAgent, AdaptivePlanner, RetryAgent.
- Input: evaluation result, score, reflection, goal tree, prompt report, context program.
- Output: reflection, hypothesis, selected strategy, self verification, adaptive plan, retry decision.

## Memory / Observability Layer

- Role: Store previous runs, debug traces, benchmark results, and prompt lifecycle artifacts.
- Included components: MemoryManager, MemoryRetrieval, DebugReportManager, BenchmarkRunner, ReportGenerator.
- Input: full execution state, prompt previews, output paths, metrics, retry results.
- Output: history records, debug report, prompt preview, benchmark JSON, comparison reports.
