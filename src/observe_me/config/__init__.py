"""Config module."""

from .config import (
    configure_app,
    get_app_settings,
)

__version__ = '0.1.0'

__all__ = [
    __version__,
    configure_app.__name__,
    get_app_settings.__name__,
]
