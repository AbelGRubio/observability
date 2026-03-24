"""Api routes definition."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from observe_me.config import __version__

api_router = APIRouter()


@api_router.get("/health")
def health() -> JSONResponse:
    """Check if everything is working."""
    status_code = 200
    return JSONResponse(content={"version": __version__}, status_code=status_code)
