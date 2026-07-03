# Code Reviews

## Review Policy

Code review focuses on behavioral regressions, unclear boundaries, missing validation, and missing tests.

## Current Review Summary

- Agent boundaries are mostly clear.
- ExecutionEngine centralizes workflow order.
- ToolRegistry decouples execution from concrete classes.
- ContextProgramBuilder improves separation between context and prompt compilation.
- DebugReportManager improves observability.

## Known Review Risks

- Context Program schema is not yet validated.
- Provider compiler behavior needs targeted tests.
- Some fallback paths are intentionally permissive and should be hardened before production.
- Benchmark reports should not be treated as absolute image quality evaluation.

## Review Checklist

- Does the change stay inside allowed files?
- Does it preserve existing workflow compatibility?
- Does it update relevant documentation?
- Does it avoid leaking `.env` or token values?
- Does it keep runtime outputs out of curated docs?
- Does `compileall` pass?

## TODO

Add per-sprint review links when the project starts using pull requests.
