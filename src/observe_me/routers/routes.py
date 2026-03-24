"""Api routes definition."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from observe_me.config import __version__

v1_router = APIRouter()


@v1_router.get("/route")
def route() -> JSONResponse:
    """Check if everything is working."""
    status_code = 200
    return JSONResponse(content={"version 200": __version__}, status_code=status_code)
