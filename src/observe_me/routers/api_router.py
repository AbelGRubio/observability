"""Api routes definition."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from opentelemetry import trace

import observe_me
from observe_me.config import __version__
from observe_me.core.logger_api import get_logger

logger = get_logger(__name__)

api_router = APIRouter()


@api_router.get("/health")
def health() -> JSONResponse:
    """Check if everything is working."""
    status_code = 200
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("obtain version") as span:
        span.add_event("obtain version from module package", {"package": observe_me.__name__})

        logger.info("Inside obtain version")
        logger.debug("Inside obtain version")

        span.add_event("Version obtained", {"version": f"{__version__}", "result": "ok"})
    logger.info("Getting version")
    return JSONResponse(content={"version": __version__}, status_code=status_code)
