# Security Considerations

This document is intended for **human developers and security reviewers**. It covers known vulnerability patterns in the AI/MCP ecosystem that are directly relevant to this project's deployment model.

> For AI agent behavioral constraints (what the agent must never execute), see [AGENTS.md](AGENTS.md).

---

## 1. Model Context Protocol (MCP) — Exposure Risk

MCP was designed for **local, trusted communication** between an agent and its tools. It is not designed to be exposed publicly.

**Risk:** Exposing an MCP server over the internet — even behind a reverse proxy without proper authentication — allows unauthenticated attackers to:
- Invoke registered tools directly, bypassing the agent entirely
- Read environment variables and secrets accessible to the server process
- Pivot into the internal network via tool side effects

**Guardrails:**
- `SERVER__HOST` must be `localhost` (default) or an internal VPC address — **never** `0.0.0.0` in production
- All MCP endpoints must sit behind JWT authentication (`SERVER__JWT_PROTECTED=true`)
- Never expose the MCP management interface or inspector port publicly
- In Docker: do not bind MCP ports to `0.0.0.0` unless behind an authenticated load balancer

---

## 2. STDIO Transport — Prompt Injection & RCE Risk

The MCP `stdio` transport executes tools as subprocesses. If user-controlled input reaches tool arguments without sanitization, it can trigger command injection or unintended filesystem access.

**Guardrails:**
- Prefer `streamable-http` transport in production (`SERVER__TRANSPORT=streamable-http`)
- Use `stdio` only for local development or fully trusted, sandboxed environments
- Never pass raw user input directly to shell-invoking tools without explicit sanitization
- Validate and sanitize all tool inputs at the boundary — treat LLM output as untrusted

---

## 3. Supply Chain — Dependency Poisoning

The AI/ML Python ecosystem has been a repeated target for supply chain attacks. Malicious packages have been pushed to PyPI by compromising CI/CD scanners or hijacking maintainer accounts, with payloads targeting:
- API keys and tokens (OpenAI, AWS, etc.)
- Cloud credential files (`~/.aws/credentials`, `kubeconfig`)
- Persistent backdoors in container and systemd environments

**Guardrails:**
- All dependencies are managed via `uv` with a locked `uv.lock` — never install unpinned packages in production
- Production builds pull from the internal **Artifactory** registry, not PyPI directly
- Regularly audit `uv.lock` for unexpected version changes, especially for AI gateway and proxy packages
- Run containers as non-root, with read-only filesystem where possible
- Do not mount `.env`, `~/.aws`, or `~/.kube` into containers

---

## 4. RAG / Vector Pipelines — Path Traversal & Injection

If this MCP server is extended with RAG or vector ingestion capabilities, file upload and ingestion pipelines are high-risk:

**Guardrails:**
- Validate and normalize all file paths before writing to disk — reject sequences containing `../`
- Restrict ingestion to an explicit allowlist of file types and sizes
- Run ingestion workers in isolated processes with no access to credentials or the host filesystem
- Never expose raw vector search results to the LLM without output filtering

---

## 5. Credential & Secret Hygiene

| Asset | Storage | Agent access |
|---|---|---|
| `.env` (tokens, passwords) | Local disk, never committed | Blocked via `.copilotignore` |
| Bitbucket write token | Never stored — entered manually on push prompt | Agent cannot push (no token in push URL) |
| AWS credentials | Shell env vars only, via `awsume` — never on disk | Not available in VS Code terminal |
| Artifactory token | `.env` only | Blocked via `.copilotignore` |

See [AGENTS.md — Developer Terminal Setup](AGENTS.md#-developer-terminal-setup-one-time) for the one-time git split-credential setup and daily push workflow.

---

## 6. Security Advisory — MCP Ecosystem (CVE-2026-30617 / CVE-2026-30623)

Global Security Operations has issued an advisory for projects using MCP-enabled components. The following checks are required for any deployment of this project or projects derived from it.

> These controls map to the patterns exploited in CVE-2026-30617 (LangChain-Chatchat) and CVE-2026-30623 (LiteLLM). Even if this project does not use those libraries directly, the same architectural risk patterns apply to any MCP server.

### 6.1 MCP management endpoint must not be publicly exposed

- Confirm that no MCP administration or connection-management routes are reachable from the internet or untrusted networks.
- If the service is published via Ingress, Load Balancer, reverse proxy, or port-forward, verify those routes are **not** reachable externally.
- Do not assume `localhost` binding — verify the effective `SERVER__HOST` value in the running deployment, not just documentation. Default `0.0.0.0` binds to all interfaces.
- **Remediation:** Restrict to internal network / VPN only. Remove public routing rules for MCP management paths. Force `SERVER__HOST` to an internal address.

### 6.2 STDIO transport must not be enabled in production

- Verify no active MCP connections use `transport = stdio`.
- `stdio` spawns subprocesses directly; any path traversal or prompt injection in tool arguments can result in RCE.
- **In this project:** `SERVER__TRANSPORT` defaults to `streamable-http`. Confirm this is the value in production. Never set it to `stdio` in an internet-facing deployment.
- **Remediation:** Disable or remove any `stdio`-based connections. Migrate to `streamable-http` or `sse` transport.

### 6.3 Agent execution mode must be explicitly gated

- If the MCP server exposes tools that can be chained autonomously (agent loop), confirm this mode requires explicit user opt-in and is not enabled by default in production.
- Verify that `tools` / `tool_choice` patterns in the LLM call path do not silently activate unrestricted tool execution.
- **Remediation:** Require explicit enablement per-session. Block autonomous tool chaining at the application layer if not needed for the use case.

### 6.4 Admin UI must not be publicly accessible (if using LiteLLM or similar gateway)

- If this project uses LiteLLM or any AI gateway with a management dashboard, verify the UI is not reachable from the internet.
- Disable the UI entirely if not needed (e.g., `DISABLE_ADMIN_UI=true` in LiteLLM).
- If the UI is required, gate it behind SSO, VPN, or IP allowlist. Ensure SSO login routes (`/sso/*`) are also restricted.

### 6.5 MCP configuration creation/editing must be restricted to trusted actors only

- Audit which users and API keys hold administrative privileges over MCP server configuration.
- Verify that low-privilege, viewer, or external accounts cannot create, edit, or delete MCP server definitions.
- Review SSO role mappings — confirm no external user inherits an admin role by misconfiguration.
- **Remediation:** Revoke excess privileges. Correct SSO role mappings. Rotate administrative keys if prior exposure cannot be ruled out.

### 6.6 Keep AI gateway and MCP dependencies up to date

- Pin all MCP-related, LLM gateway, and AI framework dependencies in `uv.lock`.
- Regularly update to the latest stable versions — advisories in this space are frequent and patches are released quickly.
- Monitor the internal Artifactory registry for updated packages and apply them as part of the normal release cycle.

---

## 7. Mandatory Deployment Checklist

Before deploying to any non-local environment:

- [ ] `SERVER__HOST` is **not** `0.0.0.0` — bound to internal address only
- [ ] `SERVER__JWT_PROTECTED=true` — JWT middleware enabled
- [ ] `SERVER__SIGNATURE=true` — technical-headers signature middleware enabled
- [ ] `OIDC__VERIFY_TOKEN=true` — full JWT verification active
- [ ] `LOCAL_DEV=false` — production guards enabled
- [ ] `SERVER__TRANSPORT=streamable-http` — STDIO transport not used in production
- [ ] MCP management/admin routes not reachable from internet or untrusted networks
- [ ] Agent/tool execution mode requires explicit opt-in — not enabled by default
- [ ] Admin UI (if any gateway is used) disabled or behind SSO/VPN/IP allowlist
- [ ] MCP configuration write access restricted to trusted actors only — no external/viewer roles with admin privileges
- [ ] AI gateway and MCP dependencies updated to latest stable versions
- [ ] Container runs as non-root
- [ ] No `.env`, `~/.aws`, or `~/.kube` mounted into the container
- [ ] All dependencies pulled from Artifactory (not PyPI directly)
- [ ] `uv.lock` reviewed for unexpected changes since last release

---

## Reporting a Vulnerability

If you discover a security vulnerability in this project, do **not** open a public issue.
Contact with a description and reproduction steps.
