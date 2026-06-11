"""Application factory for the Observe Me FastAPI server.

This module builds and configures the API application instance,
including routing, optional authentication middleware, CORS, and
Prometheus metrics instrumentation.
"""

from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from observe_core import AuthMiddleware, SessionMiddleware
from observe_core.logger_api import get_logger
from prometheus_fastapi_instrumentator import Instrumentator

from observe_api.config import (
    __version__,
    get_app_settings,
)
from observe_api.routers import api_router, v1_router

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def define_app(add_auth: bool = False) -> FastAPI:
    """Create and configure the FastAPI application instance.

    Args:
        add_auth: Whether to attach the authentication middleware.

    Returns:
        A configured FastAPI application.

    """
    app = FastAPI(title="Observer Controller", summary="Observer controller", version=__version__)

    app.include_router(router=api_router, tags=["Router 1: API endpoints"])

    app.include_router(
        router=v1_router,
        tags=["Router 2: Endpoints"],
    )

    app.add_middleware(SessionMiddleware)

    if add_auth:
        app.add_middleware(AuthMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_app_settings().cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Instrumentator().instrument(app).expose(app)

    logger.info("Define fastapi server.")
    return app
