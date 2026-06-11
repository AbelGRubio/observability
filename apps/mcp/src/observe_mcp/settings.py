"""This module provides config for working with Observer MCP Assistant."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__version__ = "0.1.0"


class AppSettings(BaseSettings):
    """Root application settings. Composes all section settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        env_ignore_empty=True,
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
        env_prefix_target="all",
    )

    local_dev: bool = Field(
        default=False, alias="LOCAL_DEV", description="Enable local development mode (disables some production guards)"
    )
    app_env: str = Field(
        default="local", alias="APP_ENV", description="Deployment environment (e.g., local, local-aws, dev, prod)"
    )
    log_level: str = Field(
        default="INFO", alias="LOG_LEVEL", description="Logging level (e.g., DEBUG, INFO, WARNING, ERROR)"
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return the cached application settings instance."""
    return AppSettings()
