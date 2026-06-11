"""Versioned API route definitions."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from observe_core.logger_api import get_logger
from opentelemetry import trace

from observe_api.config import __version__

v1_router = APIRouter()
logger = get_logger(__name__)


@v1_router.get("/route")
def route(name: str) -> JSONResponse:
    """Return a sample versioned response for the given name."""
    status_code = 200
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("my-operation") as span:
        span.add_event("Start doing operation")

        # Placeholder business logic.
        user_id = 123

        span.add_event("User processed", {"user.id": f"{name}:{user_id}", "result": "ok"})
    logger.info("Doing things here")
    return JSONResponse(content={f"{name}, the version is": __version__}, status_code=status_code)
