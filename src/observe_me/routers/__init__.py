"""Definicion de los routes de la api."""

from .api_router import api_router
from .routes import v1_router

__all__ = ["api_router", "v1_router"]
