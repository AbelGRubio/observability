# observe_core

Shared Python library used across backend projects in this monorepo.

## Purpose

- Provide reusable core modules for API, MCP, and Agent services
- Centralize cross-cutting concerns (logging, security, settings, observability)
- Reduce duplicated code between independent apps

## Location in the Monorepo

- Library root: `libs/observe_core`
- Source code: `libs/observe_core/src/observe_core`

## Used By

- `apps/api`
- `apps/mcp`
- `apps/agent`

## Development

```bash
cd libs/observe_core
uv sync
```

This library is consumed as a local path dependency in each Python app's `pyproject.toml`.
