"""Api routes definition."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from opentelemetry import trace

from observe_me.config import __version__
from observe_me.core.logger_api import get_logger

v1_router = APIRouter()
logger = get_logger(__name__)


@v1_router.get("/route")
def route(name: str) -> JSONResponse:
    """Check if everything is working."""
    status_code = 200
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("my-operation") as span:
        span.add_event("Start doing operation")

        # tu lógica
        user_id = 123

        span.add_event("User processed", {"user.id": f"{name}:{user_id}", "result": "ok"})
    logger.info("Doing things here")
    return JSONResponse(content={f"{name}, the version is": __version__}, status_code=status_code)
