# API Service

FastAPI backend service for the monorepo.

## Purpose

- Exposes REST endpoints
- Implements API-level business logic
- Reuses shared modules from `observe_core`

## Location in the Monorepo

- Source code: `apps/api/src/observe_api`
- Service entrypoint: `apps/api/src/__main__.py`
- Shared library dependency: `libs/observe_core`

## Requirements

- Python 3.13
- `uv`

## Setup

```bash
cd apps/api
uv sync
```

## Run Locally

```bash
cd apps/api
PYTHONPATH=src uv run python src/__main__.py
```

Default local endpoint:

- `http://127.0.0.1:8000`

Containerized endpoint from compose:

- `http://localhost:8010`

## Docker Build

```bash
cd apps/api
make docker-build
```

## Notes

- Docker Compose deployment for this service lives in `infra/compose.yaml`.
- Observability integrations (logs/traces/metrics) are configured from the infrastructure layer.
