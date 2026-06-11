"""This module provides tools for working with Observer MCP Assistant."""

import os
import re

import httpx

from observe_mcp.configure_app import get_mcp

my_mcp_server = get_mcp()


# Farewell detection — used to short-circuit with a goodbye message.
_FAREWELL_RE = re.compile(
    r"\b(bye|goodbye|ciao|later|see\s+you|hasta\s+luego|au\s+revoir|arrivederci|auf\s+wiedersehen)\b",
    re.IGNORECASE,
)

# Common single-word greetings/filler and ID label prefixes to strip before extracting the name.
# DNI:? / NIF:? handles inputs like "DNI 12345678A".
_NOISE_RE = re.compile(
    r"\b(hello|hi|hey|howdy|hola|ciao|bonjour|salut|bonsoir|buongiorno|buonasera|"
    r"hallo|ol\u00e1|saludos|buenas|good\s*(morning|afternoon|evening|day)|"
    r"guten\s*(morgen|tag|abend)|bom\s*(dia|tarde|noite)|DNI:?|NIF:?)\b",
    re.IGNORECASE,
)

# DNI/NIF pattern: 7-9 digits followed by a letter (e.g. 12345678A, 666666666J).
_DNI_RE = re.compile(r"\b[0-9]{7,9}[A-Za-z]\b")


@my_mcp_server.tool(
    name="hello_world",
    description=(
        "Observer MCP Assistant entry point. Greets the user, introduces itself, "
        "and collects the name and national ID (DNI/NIF) needed to personalize "
        "subsequent financial service calls."
    ),
)
async def hello_world(user: str) -> str:
    """Greets the user and collects their name and national ID (DNI/NIF).

    This is the entry-point tool for the Observer MCP Assistant.  It introduces
    the assistant and, if the caller has not yet provided both a full name and
    a national ID, it asks for them up-front so that all subsequent tool calls
    (account balances, transactions, card movements, etc.) can be personalized
    without prompting for identity again.

    Logic:
      - Farewell keyword detected  -> polite goodbye.
      - DNI present, name missing  -> ask for the name.
      - Name present, DNI missing  -> ask for the DNI.
      - Both present               -> confirm and invite next question.
      - Neither present            -> introduce assistant and ask for both.

    Args:
        user (str): Any input from the user -- a greeting, a name, an ID,
                    or all three together (e.g. "hola Juan Garcia 12345678A").

    Returns:
        str: A short, focused reply from the Observer MCP Assistant.
    """
    # Farewell short-circuit.
    if _FAREWELL_RE.search(user):
        return "Goodbye! The Observer MCP Assistant is always here when you need it."

    has_dni = bool(_DNI_RE.search(user))
    # Strip greeting noise and DNI token; what remains is the candidate name.
    name_part = _NOISE_RE.sub("", user)
    name_part = _DNI_RE.sub("", name_part).strip()
    has_name = len(name_part) > 1

    if not has_name and not has_dni:
        return (
            "Hi! I'm the **Observer MCP Assistant**, your digital observer helper.\n"
            "To get started, please tell me your **full name** and **national ID (DNI/NIF)**."
        )
    if not has_dni:
        return (
            f"Hi, {name_part}! I'm the **Observer MCP Assistant**.\n"
            "Could you also provide your **national ID (DNI/NIF)** so I can access your account?"
        )
    if not has_name:
        return (
            "I'm the **Observer MCP Assistant**. I have your ID -- "
            "could you also share your **full name** so I can address you correctly?"
        )

    return f"Welcome, {name_part}! I'm the **Observer MCP Assistant**. Identity confirmed. How can I help you today?"


@my_mcp_server.tool(
    name="execute_route",
    description=("Just call to another RestAPI and get its version."),
)
async def execute_route(name: str) -> str:
    """Just call to another RestAPI and get its version.

    Returns:
        str: A short, focused reply from the Observer MCP Assistant.
    """
    # Build target URL from environment or use localhost default.
    base_url = os.getenv("OBSERVER_ROUTE_BASE", "http://observe_api:8000")
    route_url = f"{base_url.rstrip('/')}/route"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(route_url, params={"name": name})
            resp.raise_for_status()

            # Prefer JSON 'version' field if present, otherwise use text.
            try:
                data = resp.json()
                if isinstance(data, dict) and "version" in data:
                    return f"Remote route response: {data!s}"
            except Exception:
                pass

            text = resp.text.strip()
            if text:
                return f"Remote route response: {text}"

            return "Remote route returned no content."
    except httpx.HTTPStatusError as e:
        return f"Remote route returned HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"Error contacting remote route: {e}"
