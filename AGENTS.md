# Observe me - AI Agent Development Guidelines

This document is the **behavioral mandate** for AI agents and developers working on the Observe_me repository. It defines the canonical workflows, architecture rules, quality gates, and hard constraints.

**CRITICAL**: Before making any code change, you MUST also read [CONVENTIONS.md](CONVENTIONS.md) — it contains the tech stack, code conventions, and structural reference that all agents are required to follow.

---

## 🚀 Core Workflows

### 1. Environment Setup & Onboarding
- **Initial setup**: Always run `make setup` first. This triggers `observe-me env setup-credentials` (interactive Python CLI).
- **Portability**: All scripts and Makefile targets must be POSIX-compliant (WSL, Linux, macOS). Use Python for complex logic — never long bash in Makefiles.
- **Credential safety**: Github/Gitlab tokens live in `.env` and are backed up to `.env.backup` on `make clean`. Never commit these files.

### 2. Monorepo Architecture
- **`observe-me`** = root package (source of truth — all logic lives here).
- **Dev deps**: path-based (`path = "../.."`, editable). **Production**: switch to Artifactory registry index.
- **`settings_definitions.yaml`** lives in `src/observe_me/` (bundled as package data). Never copy it to app or runtime — resolved via `$(wildcard)` from the installed package.
- **Env propagation**: Root `.env` variables must be exported to sub-processes. `observe-me-app/Makefile` looks for a parent `.env` if local one is missing.
- **App is standalone**: `observe-me-app` must work outside the monorepo. From the monorepo, run `make setup` from root first (bootstraps credentials without auth).

### 3. Quality Assurance (CI)
- **Always run `make ci` before proposing any change.** Includes:
  - `checkmake` — Makefile linter (strict target line limits).
  - `ruff` — Python linter (complexity ≤ 10, line length 120).
  - `pyrefly` — Type checker.
  - `pytest` — Full test suite.

### 4. Local Containerization
- **`make run-container`** uses `Dockerfile.local` to build and run the MCP server locally.
- `Dockerfile.local` must copy the entire parent project so `uv sync` resolves the path dependency (`..`).
- **Dev mode only** — for production, `Dockerfile` must use Artifactory index instead of local relative paths.

---

## 🛠 Technical Standards

### Makefile Patterns
- **Complex logic → Python**: Delegate to `uv run observe-me ...` or `uv run scripts/...`. Never write long bash in targets.
- **No shell scripts** — use Make targets + Python CLI only (Windows/WSL compatibility).
- **Portable `sed`**: `sed "..." file > file.tmp && mv file.tmp file` — never `sed -i`.
- **Export vars**: Use `export` so child processes receive `.env` variables.
- **Target line limit**: Keep targets short (checkmake enforces this).

#### Dynamic path resolution (app & runtime context)
```makefile
# Editable install (monorepo ../src) takes priority; falls back to published package in .venv
ENV_SPEC      := $(or $(firstword $(wildcard ../src/observe_me/settings_definitions.yaml .venv/lib/*/site-packages/observe_me/settings_definitions.yaml)),settings_definitions.yaml)
ENV_GENERATED := $(or $(firstword $(wildcard ../src/observe_me/core/env/datamodel.py .venv/lib/*/site-packages/observe_me/core/env/datamodel.py)),src/observe_me/core/env/datamodel.py)
```
Runtime projects (`mcp-runtime-generated/`) use `../../src/...` (two levels deep).

#### Dynamic binary resolution (app & runtime context)
```makefile
# Precedence: monorepo root venv → app venv → uv fallback
_OBSERVE_BIN := $(or $(firstword $(wildcard ../.venv/bin/observe-me .venv/bin/observe-me)),uv run observe-me)
ENV_CLI := $(_OBSERVE_BIN) env
```
Apply this pattern to **all** targets invoking `observe-me` CLI from an app/runtime context. Never rely on PATH.

### Credential Verification
- **Gitlab**: Verify tokens via HTTP HEAD request, detecting SSO redirects (expired credentials).
- **Github**: Permissive — if definitive validation fails due to network context, skip with a warning (don't hard-fail) as long as the Git remote is functional.

### Git Hygiene
- **Branch naming**: `feature/XX-short-description`.

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
- `git push` → VS Code Source Control panel prompts for username + write token each time
- Token is never stored on disk for push

### Git — daily push workflow (external terminal only)

```zsh
# Stage and commit (always in your external terminal, never via the agent)
git add -p
git commit -m "feat(XX): short description"

# Push — VS Code will prompt for your write token, or use the CLI:
git push origin feature/XX-your-branch
# Enter: username → YOUR_GITHUB_USER
# Enter: password → YOUR_WRITE_TOKEN
```

### AWS — session activation (external terminal only)

```zsh
# Activate your AWS profile via awsume (credentials stay in this shell session only)
awsume your-profile-name

# Verify (optional)
aws sts get-caller-identity

# Now run any aws command you need, e.g.:
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin YOUR_ECR_URL
```

Credentials injected by `awsume` are **shell environment variables** (`AWS_ACCESS_KEY_ID`, `AWS_SESSION_TOKEN`) — they exist only in that terminal session and expire automatically. The VS Code terminal never has them.

---

## ✅ Quality Gates

Before suggesting or applying any change, verify it passes:

1. `ruff check` — linting (complexity ≤ 10, all rule groups in `pyproject.toml`).
2. `pyrefly check` — type checking.
3. `pytest` — all tests pass.
4. `checkmake` — all Makefile targets within line limits.

---

## 🚫 Hard Constraints

- **NEVER** use `print()` — use `loguru` (`get_logger`) or `rich`.
- **NEVER** use `pip` — always `uv`.
- **NEVER** use `sed -i` — use the portable `sed ... > file.tmp && mv file.tmp file` pattern.
- **NEVER** use shell scripts — use Make targets + Python CLI only.
- **NEVER** commit `.env`, `.env.backup`, or any secrets/tokens.
- **NEVER** add unnecessary abstractions — keep complexity minimal.
- **NEVER** add error handling for scenarios that cannot happen.
- **NEVER** hardcode paths to package files — use `$(wildcard)` dynamic resolution.
- **NEVER** add `setup-credentials` to non-interactive targets like `doctor`.
- **NEVER** run git write commands (`commit`, `push`, `rebase`, `reset`, `merge`) — these are reserved for the human developer.
- **NEVER** run any `aws` CLI command — AWS credentials are not available in the VS Code terminal; commands will fail or block.
- **NEVER** read `.git/config`, `~/.aws/credentials`, or any file containing remote credentials.
- **NEVER** modify infrastructure files (`Jenkinsfile.genAI`, `component_config.yml`) — these are managed by the platform team and excluded from agent context via `.copilotignore`.
