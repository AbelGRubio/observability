# Observability — Style Guide

This document summarises the coding conventions, commit style, and documentation standards for the Observability project.

For the full technical reference (tech stack, Makefile patterns, type rules) see [CONVENTIONS.md](CONVENTIONS.md).

---

## Python

| Rule | Detail                                                                           |
|---|----------------------------------------------------------------------------------|
| Python version | 3.13+                                                                            |
| Formatter | `ruff format` — 120-char line length                                             |
| Linter | `ruff check` — all rule groups in `pyproject.toml`                               |
| Type checker | `pyrefly` — all functions must have type annotations                             |
| Complexity limit | Cyclomatic complexity ≤ 10 per function                                          |
| Logging | `from observe_me.core import get_logger` — never `print()` or `logging` directly |
| Package manager | `uv` only — never `pip`                                                          |

### Imports

- Standard library first, then third-party, then local — each group separated by a blank line.
- Do **not** use wildcard imports (`from module import *`).

### Type annotations

- All function parameters and return types must be annotated.
- Use `str | None` (union syntax, Python 3.10+), not `Optional[str]`.

### Docstrings

Use Google-style docstrings for public functions:

```python
def my_function(param: str) -> str:
    """Short one-line summary.

    Args:
        param: Description of the parameter.

    Returns:
        Description of what is returned.

    Raises:
        ValueError: When the input is invalid.
    """
```

---

## Makefile

- Use `sed "..." file > file.tmp && mv file.tmp file` — never `sed -i` (not portable).
- Every phony target must declare `.PHONY`.
- Target help strings (`## description`) must be present for all user-facing targets.

---

## Git & Commits

| Convention | Example |
|---|---|
| Branch names | `feature/short-description` |
| Commit style | [Conventional Commits](https://www.conventionalcommits.org/) |

Commit message format:

```
feat: include new feature 

Body explaining why this change is needed and what it does.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`.

---

## MCP Tools

- Tool names in `snake_case`.
- Short, clear `description` — this is what the AI reads to decide when to call the tool.
- Always return `str` (use `json.dumps` for structured data).
- Place `@requires_signature` **below** `@mcp.tool()`, never above.
- Keep each tool function ≤ 20 lines; extract helpers if needed.

---

## Documentation

- All user-facing docs live in `docs/` and are served by MkDocs.
- Use named anchors for cross-references.
- Code blocks must specify the language (`python`, `bash`, `yaml`, etc.).
- Do not duplicate content — link to the canonical location instead.
