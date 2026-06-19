# Frontend App

Next.js frontend for the observability monorepo.

## Purpose

- Provide the web UI for interacting with platform services
- Connect to backend/API endpoints exposed by other apps
- Host frontend-specific pages, components, and API routes

## Location in the Monorepo

- App root: `apps/front`
- Main source: `apps/front/app`

## Requirements

- Node.js 18+
- `pnpm`

## Setup

```bash
cd apps/front
pnpm install
```

## Run Locally

```bash
cd apps/front
make front
```

or

```bash
cd apps/front
pnpm run dev-frontend
```

Default local endpoint:

- `http://localhost:3000`

## Build

```bash
cd apps/front
pnpm run build
pnpm run start
```

## Notes

- This project is independent from Python apps under `apps/`, but it is deployed alongside them in the monorepo workflow.
- Shared backend logic is implemented in `libs/observe_core` and consumed by Python services (`api`, `mcp`, `agent`).
- Infrastructure and compose assets are managed from `infra/` at repository root.
