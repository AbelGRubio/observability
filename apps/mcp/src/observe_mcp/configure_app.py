"""Observe MCP Server Core Initialization.

========================================================================================================================
Name:         observe_mcp/configure_app.py
Description:  This module acts as the central assembly point for the MCP server. It:
                1. Instantiates the FastMCP server.
                2. Conditionally attaches authentication middleware.
                3. Registers system health routes.
                4. Populates the server with tools discovered by the loader.
Date:         2026-01-12 13:34:48
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from functools import lru_cache

from fastmcp import FastMCP
from fastmcp.server.http import StarletteWithLifespan
from observe_core import get_logger
from observe_core.security.session import SessionMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from prometheus_fastapi_instrumentator import Instrumentator
from observe_mcp.settings import __version__, get_settings

logger = get_logger(__name__)


def load_tools() -> None:
    """Load tools, import here yours modules from src."""
    import observe_mcp.tools as tools

    logger.info(f"Loaded tools from {tools.__name__}")


@lru_cache(maxsize=1)
def get_mcp() -> FastMCP:
    """Get mcp instance configured."""
    mcp_instance = FastMCP(
        name="Observe Runtime",
        instructions="Secure MCP server with OAuth authentication",
    )
    logger.info("Create FastMCP instance.")
    return mcp_instance


@lru_cache(maxsize=1)
def get_asgi_app() -> StarletteWithLifespan:
    """Get the asgi app from mcp."""
    mcp_ = get_mcp()
    app_instance = mcp_.http_app()
    settings = get_settings()

    app_instance.add_middleware(SessionMiddleware, local_dev=settings.local_dev)

    # Middlewares condicionales
    # if not settings.local_dev:
    #     logger.info("added Auth middleware")
    #     app_instance.add_middleware(AuthMiddleware)

    app_instance.add_route("/health", health_check, methods=["GET"], name="health")

    Instrumentator().instrument(app_instance).expose(app_instance)

    logger.info("Added custom route to asgi FastMCP instance.")

    return app_instance


async def health_check(request: Request) -> Response:  # noqa: RUF029
    """Server Health Check Endpoint.

    Provides basic metadata about the running instance, such as the
    current version and application name. Useful for monitoring
    and load balancer heartbeats.

    Args:
        request (Request): The incoming Starlette request object.

    Returns:
        PlainTextResponse: A JSON-formatted string containing status info.
    """
    status = {
        "version": f"{__version__}",
        "app_name": "Observe mcp",
    }
    return JSONResponse(status)
