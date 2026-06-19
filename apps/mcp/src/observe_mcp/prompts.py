"""Prompt definitions exposed via the MCP server.

========================================================================================================================
Name:         apps/mcp/src/observe_mcp/prompts.py
Description:  Register prompt templates with the MCP server and provide
              callable prompt generators used by the runtime and tools.
Project:      Observe me
Date:         2026-06-19 00:00:00
Status:       Development

Copyright ©2026. All rights reserved.
========================================================================================================================
"""

from pathlib import Path
from typing import Any

from observe_mcp.configure_app import get_mcp

# Obtain the MCP server instance used to register prompts. The concrete type
# depends on the MCP framework; typing as `Any` avoids a hard dependency here.
my_mcp_server: Any = get_mcp()


@my_mcp_server.prompt("architect-design")
def architect_design_prompt(task_description: str) -> str:
    """Render the `architect-design` prompt from a markdown template.

    The template file `prompts/architect-design.md` is read as UTF-8 and a
    placeholder `{{TASK_DESCRIPTION}}` is replaced with the provided task
    description.

    Args:
        task_description: Short description of the architecture task provided
            by the user. This value is injected into the template.

    Returns:
        The final prompt string ready to be sent to an LLM.
    """

    # 1. Load the template relative to the package. In production the file
    # should exist under the package data (see packaging rules in pyproject).
    template_path = Path("prompts/architect-design.md")
    template = template_path.read_text(encoding="utf-8")

    # 2. Replace the placeholder with the real task description. This uses a
    # simple string replacement; template engines (Jinja2) can be used if
    # richer templating is required in future.
    final_prompt = template.replace("{{TASK_DESCRIPTION}}", task_description)

    return final_prompt
