"""Api routes definition."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from observe_me.config import __version__
from observe_me.core.logger_api import get_logger

logger = get_logger(__name__)

api_router = APIRouter()


@api_router.get("/health")
def health() -> JSONResponse:
    """Check if everything is working."""
    status_code = 200
    logger.info("Getting version")
    return JSONResponse(content={"version": __version__}, status_code=status_code)
