"""Application-level settings model."""

from observe_core.custom_settings import CustomSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class AppSettings(CustomSettings):
    """Settings used to configure the API server behavior."""

    __use_conf_file__: bool = False

    api_ip: str = Field(default="localhost", alias="api_ip")
    api_port: int = Field(default=8000, alias="api_port")
    minutes_refresh_conf: int = Field(default=1, alias="minutes_refresh_conf")
    cors_origins_: str = Field(default="*", alias="cors_origins")

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        populate_by_name=True,
    )

    @property
    def cors_origins(self) -> list[str]:
        """Return the list of allowed CORS origins."""
        return self.cors_origins_.split(",")
