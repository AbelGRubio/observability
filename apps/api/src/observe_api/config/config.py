"""Configuration settings."""

from functools import lru_cache

from observe_core.logger_api import get_logger

from observe_api.config.app_settings import AppSettings

logger = get_logger(__name__)

# Cached singleton factories.


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    """Return the global application settings singleton."""
    return AppSettings()


# Main application configuration function.


def configure_app(*, force_reload: bool = False) -> None:
    """Initialize cached settings and perform initial application configuration.

    Args:
        force_reload: If True, clears caches and reloads all configuration.
            Useful for tests or hot-reload scenarios.

    """
    if force_reload:
        get_app_settings.cache_clear()

    try:
        # Force singleton creation so values are cached on first load.
        _ = [
            get_app_settings(),
        ]

        logger.info("Configuration loaded.")
    except Exception:
        logger.error("Error loading configuration")
