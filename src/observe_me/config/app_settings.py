"""# src/config/app.py."""

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from observe_me.config.custom_settings import CustomSettings


class AppSettings(CustomSettings):
    """Docs."""

    __use_conf_file__: bool = True

    api_ip: str = Field(default="localhost", alias="api_ip")
    api_port: int = Field(default=5000, alias="api_port")
    minutes_refresh_conf: int = Field(default=1, alias="minutes_refresh_conf")
    cors_origins_: str = Field(default="*", alias="cors_origins")

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        populate_by_name=True,
    )

    @property
    def cors_origins(self) -> list:
        """Get listing cors."""
        return self.cors_origins_.split(",")
