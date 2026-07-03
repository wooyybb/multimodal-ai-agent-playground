# AI Usage

## Codex Usage

Codex was used as an implementation and documentation partner across the project. The workflow was sprint-based: each request defined a goal, architecture, allowed files, forbidden files, requirements, documentation updates, and done definition.

## AI Collaboration Style

- The human defined sprint goals and architectural direction.
- Codex inspected the existing codebase before editing.
- Changes were kept inside the workspace.
- Forbidden files were used to reduce accidental scope creep.
- Each sprint ended with compile or import validation when possible.

## Prompt Design

The most effective prompts followed this structure:

```text
Task
-> Architecture
-> Workspace Rule
-> Files Allowed
-> Files Forbidden
-> Requirements
-> Documentation
-> Done Definition
```

## Workspace Rule

All work must stay inside `project3`. Sensitive files such as `.env` and runtime outputs must not be documented with secrets or treated as curated assets.

## Lessons Learned

- Clear file boundaries make AI-assisted coding safer.
- Architecture prompts work better than vague feature prompts.
- Documentation should be refactored regularly, not only appended.
- LLM interfaces can be designed and tested with mock/fallback behavior before real API integration.
- Shared client layers reduce duplicated mock logic across LLM-style agents.

## Future Work

- Add a public AI collaboration policy.
- Add prompt templates for future sprints.
- Add review checklist for AI-generated changes.
