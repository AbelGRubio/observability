# MCP Service

FastMCP server for tool exposure and Model Context Protocol integration.

## Purpose

- Hosts MCP tools
- Exposes the MCP-compatible ASGI application
- Connects observability and shared logic through `observe_core`

## Location in the Monorepo

- Source code: `apps/mcp/src/observe_mcp`
- Service entrypoint: `apps/mcp/src/__main__.py`
- Shared library dependency: `libs/observe_core`

## Requirements

- Python 3.13
- `uv`

## Setup

```bash
cd apps/mcp
uv sync
```

## Run Locally

```bash
cd apps/mcp
PYTHONPATH=src uv run python src/__main__.py
```

Default local endpoint:

- `http://127.0.0.1:8000`

## Docker Build

```bash
cd apps/mcp
make docker-build
```

## Notes

- This service is part of the monorepo deployment defined in `infra/compose.yaml`.
- Runtime observability is wired through OpenTelemetry components in `infra/`.
