"""Define api."""

from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from observe_me.config import (
    __version__,
    get_app_settings,
)
from observe_me.core import AuthMiddleware
from observe_me.core.logger_api import get_logger
from observe_me.routers import api_router, v1_router

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def define_app(add_auth: bool = False) -> FastAPI:
    """Define fastapi."""
    app = FastAPI(title="Observer Controller", summary="Observer controller", version=__version__)

    app.include_router(router=api_router, tags=["Router 1: API endpoints"])

    app.include_router(
        router=v1_router,
        tags=["Router 2: Endpoints"],
    )
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
