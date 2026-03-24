"""Configuration settings."""

from functools import lru_cache
from logging import getLogger

from observe_me.config.app_settings import AppSettings

logger = getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Singletons / Cached factories con lru_cache
# ──────────────────────────────────────────────────────────────────────────────


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    """Devuelve la configuración global de la aplicación (singleton)."""
    return AppSettings()



# ──────────────────────────────────────────────────────────────────────────────
# Función principal de configuración de la aplicación
# ──────────────────────────────────────────────────────────────────────────────


def configure_app(*, force_reload: bool = False) -> None:
    """Inicializa todos los singletons/cache y realiza la configuración inicial de la aplicación.

    Args:
        force_reload: Si True, fuerza la recarga de todas las configuraciones
                      (limpia la caché). Útil en tests o recarga en caliente.

    """
    if force_reload:
        get_app_settings.cache_clear()

    try:
        # Forzamos la creación de todos los singletons
        # (esto los carga en caché la primera vez)
        _ = [
            get_app_settings(),
        ]

        logger.info("Configuration loaded.")  # o usar logging
    except Exception:
        logger.error("Error loading configuration")
