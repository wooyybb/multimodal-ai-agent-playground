# Sprint 35: FastAPI Service Layer

## Objective

Expose the multi-agent framework through a FastAPI REST API while keeping the existing Gradio UI.

## Problem

The framework could be used through Gradio, but external programs needed a REST interface.

## Design Decision

Add a separate `api/` service layer with `app.py`, `routes.py`, `schema.py`, and `service.py`.

## Implementation Summary

- Added FastAPI application.
- Added `GET /`, `GET /health`, and `POST /generate`.
- Added request and response schemas.
- Added service layer function `run_generation()`.
- Updated README and documentation.

## AI Agent Concept

FastAPI acts as a service boundary around the agent framework without changing the framework internals.

## Prompt Engineering Note

The Sprint explicitly forbade framework changes, so the API was implemented as an outer layer.

## Interview Talking Points

- Gradio is for demos and human interaction.
- FastAPI is for programmatic access.
- Service Layer avoids coupling routes directly to execution internals.

## Future Work

- Authentication
- Async job queue
- Docker deployment
- File upload support
