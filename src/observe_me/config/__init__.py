"""Config module."""

from .config import (
    configure_app,
    get_app_settings,
)

__version__ = "1.0.0-b.3"

__all__ = [
    __version__,
    configure_app.__name__,
    get_app_settings.__name__,
]
