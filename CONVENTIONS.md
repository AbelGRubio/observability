# Observe me - Tech Stack & Code Conventions

This document is the **technical reference** for developers and AI agents working on the Observe me repository. It covers the stack, project structure, code conventions, and Makefile patterns. For workflows, architecture rules, and hard constraints, see [AGENTS.md](AGENTS.md).

---

## 🐍 Tech Stack

### Core dependencies (always prefer these)

| Library | Purpose | Usage                                                                              |
|---|---|------------------------------------------------------------------------------------|
| **`fastmcp`** | MCP server framework | Use `FastMCP`; tools are decorated with `@mcp.tool()`                              |
| **`typer`** | CLI commands | Create sub-apps with `typer.Typer()`, register with `app.add_typer()`              |
| **`loguru`** | Logging | `from observe_me.core.logger_api import get_logger` — never `print()` or `logging` |
| **`rich`** | Terminal output | Use `rich.console.Console` and `rich.panel.Panel` for panels/tables                |
| **`pydantic`** | Data models & settings | Use `BaseSettings` for config classes with env prefix                              |

### Dev toolchain

| Tool | Role | Key config |
|---|---|---|
| **`uv`** | Package manager | `uv run`, `uv sync`, `uv add` — never `pip` |
| **`ruff`** | Linter + formatter | Line length 120, complexity ≤ 10, Google docstrings |
| **`pyrefly`** | Type checker | Strict — always annotate all args and return types |
| **`pytest`** + `pytest-asyncio` + `pytest-cov` | Tests | Full async support, coverage reports |
| **`pre-commit`** | Git hooks | Runs ruff + checks before every commit |
| **`checkmake`** | Makefile linter | Strict target line limits — keep targets short |

### Python version
- **Python 3.13 strictly** (`requires-python = ">=3.13,<3.14"`).
- Use modern syntax: `X | Y` unions, `match` statements, `tomllib`, etc.
- Avoid `typing` module aliases that have `collections.abc` equivalents.

---

## 🗂 Project Structure

```
src/observe_me/
├── core/
│   ├── cli.py              # Main Typer app — register all sub-commands here
│   ├── logger.py           # get_logger() factory (loguru wrapper)
│   ├── dev_tools.py        # CI/check/test helper commands
│   ├── info.py             # System/env info commands
│   ├── env/                # Env datamodel system
│   │   ├── cli.py          # `observe-me env` sub-commands
│   │   ├── datamodel.py    # Auto-generated Pydantic settings (never edit manually)
│   │   ├── builder.py      # Generates datamodel.py + .env.example from YAML
│   │   ├── loader.py       # Loads .env file at runtime
│   │   └── validator.py    # Validates .env against YAML spec
│   ├── settings/
│   │   ├── server.py       # ServerConfig (Pydantic BaseSettings, prefix SERVER__)
│   │   ├── api.py          # ApiServiceSettings (prefix API__)
│   │   └── reader_yaml.py  # YAML custom_config.yaml reader
│   └── security/           # Auth middleware, security manager, IDP adapters
│       ├── auth.py
│       ├── security_manager.py
│       └── adapters/       # Keycloak, Cognito, Authentik, Logto adapters
├── services/               # MCP tool implementations
│   ├── aso.py              # ASO service tools
│   └── custom.py           # Custom/user-defined tools
├── server.py               # FastMCP server assembly (get_mcp, get_asgi_app)
├── configure_app.py        # App configuration (middleware, routes)
├── settings.py             # get_settings() — combines all sub-configs
└── settings_definitions.yaml  # Source of truth for env vars (bundled as package data)
```

### Monorepo layout

```
observe-me/                       # Root package (source of truth — all logic here)
├── src/observe_me/               # Package source
├── tests/                       # Test suite
├── make/                        # Makefile includes (*.mk)
├── scripts/                     # Python helper scripts (invoked by make targets)
├── AGENTS.md                    # Behavioral mandate for agents
├── CONVENTIONS.md               # Tech stack & conventions (this file)
├── Makefile                     # Main entry point
└── pyproject.toml               # Package metadata, dependencies, tool config
observe-me-app/                   # Stacker template scaffold (mirrors root)
observe-me-app-scaffold/          # Generated scaffold (from make scaffold-create)
mcp-runtime-generated/{name}/    # Instantiated projects (gitignored)
```

---

## ✍️ Code Conventions

### File header (required for every new Python file)

```python
"""Module title.

========================================================================================================================
Name:         path/filename.py
Description:  Brief description
Project:      Observe ne
Date:         YYYY-MM-DD HH:MM:SS
Status:       Development

Copyright ©2026. All rights reserved.
========================================================================================================================
"""
```

### Docstrings — Google style

```python
def my_function(param: str) -> bool:
    """Short one-line summary.

    Args:
        param: Description of param.

    Returns:
        Description of return value.
    """
```

### Imports — isort order

```python
# 1. future
from __future__ import annotations

# 2. standard-library
import os
from collections.abc import Callable

# 3. third-party
from loguru import logger
from pydantic import BaseSettings

# 4. first-party (observe_api)
from observe_api.core.logger_api import get_logger

# 5. local-folder
from .utils import helper
```

### Type annotations

- Always annotate **all** function arguments and return types.
- Use `from __future__ import annotations` only when needed for forward references.
- Prefer `collections.abc` over `typing` for `Callable`, `Iterator`, `Sequence`, etc.
- Use `X | Y` union syntax (Python 3.10+ style), not `Union[X, Y]`.
- Use `X | None` instead of `Optional[X]`.

### Logging

```python
from observe_api.core.logger_api import get_logger

logger = get_logger(__name__)

logger.info("Starting process: {name}", name=my_var)
logger.warning("Skipping step: {reason}", reason=details)
logger.error("Failed: {err}", err=exc)
```

### CLI commands (Typer)

```python
import typer
from observe_api.core.logger_api import get_logger

app = typer.Typer(name="my-command", help="Short description.")
logger = get_logger(__name__)


@app.command()
def my_action(param: str = typer.Argument(..., help="Description.")) -> None:
    """Short one-line summary."""
    logger.info("Running my_action with {param}", param=param)
```

Register in `src/observe_me/core/cli.py`:

```python
from observe_api.my_module import app as my_app

observe_me.add_typer(my_app)
```

### MCP tools (FastMCP)

```python
from fastmcp import FastMCP

mcp = FastMCP("observe-me")


@mcp.tool()
async def my_tool(query: str) -> str:
    """Tool description shown to the LLM client.

    Args:
        query: The input query.

    Returns:
        The result string.
    """
    ...
```

---

## 🔧 Makefile Patterns

### Philosophy
- **Short targets** — checkmake enforces line limits. Any logic beyond a few lines belongs in a Python script or CLI command.
- **No shell scripts** — everything is a Make target or `uv run observe-me ...` / `uv run scripts/...`.
- **No `sed -i`** — use `sed "..." file > file.tmp && mv file.tmp file`.
- **Export vars** — always `export` so child processes inherit `.env` variables.

### Standard target structure

```makefile
.PHONY: my-target
my-target: ## Short description shown in make help
	@uv run observe-me my-command --option value
```

### Dynamic path resolution (app & runtime context)

Files from the installed package are resolved dynamically — never hardcoded:

```makefile
# Editable install (monorepo ../src) takes priority; falls back to .venv
ENV_SPEC      := $(or $(firstword $(wildcard ../src/observe_me/settings_definitions.yaml \
                  .venv/lib/*/site-packages/observe_me/settings_definitions.yaml)),settings_definitions.yaml)
ENV_GENERATED := $(or $(firstword $(wildcard ../src/observe_me/core/env/datamodel.py \
                  .venv/lib/*/site-packages/observe_me/core/env/datamodel.py)),src/observe_me/core/env/datamodel.py)
```

> Runtime projects in `mcp-runtime-generated/` are two levels deep — use `../../src/...` instead of `../src/...`.

### Dynamic binary resolution (app & runtime context)

Never rely on PATH for the `observe-me` binary:

```makefile
# Precedence: monorepo root venv → app venv → uv fallback
_OBSERVE_BIN := $(or $(firstword $(wildcard ../.venv/bin/observe-me .venv/bin/observe-me)),uv run observe-me)
ENV_CLI    := $(_OBSERVE_BIN) env
```

Apply this pattern to **all** targets that invoke `observe-me` CLI from app or runtime context.

---

## 🐳 Local Container Testing

The local container workflow uses `Dockerfile.local` (not the production `Dockerfile`).

### Workflow

**Terminal 1** — start the server:
```sh
make run-container
```

**Terminal 2** — verify it is reachable:
```sh
make simple-client
```

### Key differences vs production (`Dockerfile`)

| | `Dockerfile.local` | `Dockerfile` (production/AWS) |
|---|---|---|
| Platform | `--platform linux/amd64` (Rosetta 2 on Mac) | Native ARM64 (AWS Agent Core) |
| Cmd | `python app.py` | `uvicorn` / `opentelemetry-instrument` |
| Env | `--env-file .env` + `-e SERVER__HOST=0.0.0.0` | Injected by runtime |

### Why `--platform linux/amd64` in `Dockerfile.local`

Docker Desktop on Apple Silicon does not expose some newer ARMv9 CPU features
(SME2, SVE2p1, etc.) to Linux ARM64 containers. Libraries with Rust-compiled
binaries (e.g. `cryptography`) use those instructions → **SIGILL** (exit 132).
Running as `linux/amd64` under Rosetta 2 avoids this. Production ARM64 Linux
machines (AWS) expose all features natively — no issue there.

### `SERVER__HOST` override

The `.env` file typically has `SERVER__HOST=localhost`, which makes the server
bind only inside the container and become unreachable from the host. The
`docker run` command overrides it with `-e SERVER__HOST=0.0.0.0`.

### OTel warnings

Lines like `Failed to export logs to localhost:4317` are benign — there is no
OpenTelemetry collector running locally. They do not affect functionality.

---

## ⚙️ Settings & Configuration

Settings are composed from multiple Pydantic `BaseSettings` classes, each with a distinct env prefix:

| Class | File | Prefix | Purpose |
|---|---|---|---|
| `ServerConfig` | `core/settings/server.py` | `SERVER__` | Host, port, auth mode, CORS |
| `ApiServiceSettings` | `core/settings/api.py` | `API__` | External API URLs, timeouts |
| *(generated)* | `core/env/datamodel.py` | varies | Auto-generated from `settings_definitions.yaml` |

All configs are combined in `settings.py` via `get_settings()`.

---

## 🔐 Security

- Auth middleware is in `core/security/auth.py`.
- IDP adapters (Keycloak, Cognito, Authentik, Logto) live in `core/security/adapters/`.
- The active IDP is chosen at runtime via `SecurityManager` (`core/security/security_manager.py`).
- OAuth2/OIDC token validation is handled per-adapter — never implement custom crypto.

### Git Security (agent constraints)
The repository remote is configured with **split credentials**:
- **Fetch URL** carries a read-only token — pull/fetch work silently.
- **Push URL** carries no token — any push attempt will block waiting for credentials the agent cannot supply.

As an agent you MUST:
- **NEVER** execute `git commit`, `git push`, `git rebase`, `git reset`, `git merge`, `git push --force`, or any variant — using full path (`/usr/bin/git`), `command git`, `\git`, or any other bypass technique.
- **NEVER** modify or inspect the fetch or push remote URL (`git remote set-url`, `git remote -v`).
- **NEVER** call `git credential`, `git config credential.*`, or any command that reads, writes, or manipulates stored credentials.
- **NEVER** read `.git/config` to discover remote URLs or tokens.
- **ALLOWED**: Show the git command in a code block so the user can copy and run it manually in their external terminal.
- All write operations (commit, push, rebase) are the exclusive responsibility of the human developer.

### AWS Security (agent constraints)
AWS credentials are **never stored on disk** in this project. They are injected into the developer's external shell session only via `awsume` (short-lived STS tokens), and are not available in the VS Code terminal where the agent runs.

As an agent you MUST:
- **NEVER** run any `aws` CLI command — read or write, local or remote. The VS Code terminal has no AWS credentials; commands will fail or block.
- **NEVER** attempt to read `~/.aws/credentials`, `~/.aws/config`, or any file that may contain AWS keys.
- **NEVER** call `awsume`, `aws configure`, or `aws sts` to attempt credential discovery.
- **ALLOWED**: Show the `aws` or `awsume` command in a code block so the user can run it manually in their external terminal where credentials are available.

---

## 🖥 Developer Terminal Setup (one-time)

> Run all commands below in an **external terminal** (iTerm2 / macOS Terminal) — NOT in the VS Code integrated terminal.
> The agent only has access to the VS Code terminal; your external terminal is the secure boundary for all write operations.

### Git — split credentials (read fetch / prompt push)

```zsh
# 1. Set fetch URL with your read-only github token
git remote set-url origin https://YOUR_USER:READ_ONLY_TOKEN@github.com/ORG/REPO.git

# 2. Set push URL without any token — git will prompt on every push
git remote set-url --push origin https://github.com/ORG/REPO.git

# 3. Disable local credential caching for push
git config --local credential.helper ""
```

After this setup:
- `git fetch` / `git pull` → silent, uses read-only token
- `git push` → VS Code Source Control panel or external terminal prompts for write token each time
- Token is never stored on disk for push

### Git — daily push workflow (external terminal only)

```zsh
# Stage and commit
git add -p
git commit -m "feat(XX): short description"

# Push — enter your write token when prompted
git push origin feature/XX-your-branch
# username: YOUR_GITHUB_USER
# password: YOUR_WRITE_TOKEN
```

### AWS — session activation (external terminal only)

```zsh
# Activate your AWS profile — credentials stay in this shell session only
awsume your-profile-name

# Verify
aws sts get-caller-identity

# Example: ECR login
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin YOUR_ECR_URL
```

Credentials injected by `awsume` are shell environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SESSION_TOKEN`) — they exist only in that terminal session and expire automatically. The VS Code terminal never has them.
