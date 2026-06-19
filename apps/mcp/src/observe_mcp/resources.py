"""MCP resource handlers exposing local markdown documentation.

========================================================================================================================
Name:         apps/mcp/src/observe_mcp/resources.py
Description:  Provide MCP resource endpoints that serve markdown files from
              the `resources/` directory. These functions are registered on
              the MCP server and return raw markdown content.
Project:      Observe me
Date:         2026-06-19 00:00:00
Status:       Development

Copyright ©2026. All rights reserved.
========================================================================================================================
"""

from pathlib import Path
from typing import Any

from observe_mcp.configure_app import get_mcp

# MCP server instance used to register resource handlers. The concrete type
# is provided by the MCP framework; using `Any` avoids a hard dependency.
my_mcp_server: Any = get_mcp()


def load_md_file(filename: str) -> str:
    """Load a markdown file from the `resources/` directory.

    Args:
        filename: Relative filename under the `resources/` directory.

    Returns:
        File content as a UTF-8 string. If the file does not exist, returns
        a simple error message string (suitable for debugging).
    """

    # Build a path relative to the package execution root. In production the
    # `resources/` directory should be included as package data.
    filepath = Path("resources") / filename

    if not filepath.exists():
        return f"Error: No se encontró el archivo {filename}"

    return filepath.read_text(encoding="utf-8")


@my_mcp_server.resource("file://docs/{filename}", mime_type="text/markdown")
def read_documentation(filename: str) -> str:
    """Resource handler: return arbitrary markdown documentation by filename.

    Example URI: `file://docs/software_engineering_principles.md`.
    """

    return load_md_file(filename)


@my_mcp_server.resource("file://docs/conventions", mime_type="text/markdown")
def read_conventions() -> str:
    """Return the repository `CONVENTIONS.md` content as a resource.

    This handler maps the logical resource `file://docs/conventions` to the
    physical file `resources/conventions.md`.
    """

    return load_md_file("conventions.md")


@my_mcp_server.resource("file://docs/agents", mime_type="text/markdown")
def read_agents() -> str:
    """Return the `AGENTS.md` documentation from the resources folder."""

    return load_md_file("agents.md")
