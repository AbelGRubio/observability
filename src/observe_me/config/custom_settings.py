"""Application configuration using Pydantic Settings."""

import configparser
import os
import warnings
from logging import getLogger
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

logger = getLogger(__name__)


def load_cfg_file(config_file: Path) -> dict[str, Any]:
    """Load the CFG configuration file and flatten it into a dictionary."""
    if not os.path.isfile(config_file):
        msg = f"Config file does not exist: {config_file}. Using default configuration"
        warnings.warn(msg, UserWarning, stacklevel=2)
        logger.warning(msg)
        return {}

    parser = configparser.ConfigParser()
    parser.read(config_file)

    data: dict[str, Any] = {}

    for section in parser.sections():
        for key, value in parser.items(section):
            data[key] = value

    return data


class CustomSettings(BaseSettings):
    """Base settings class that loads values from a CFG file."""

    __use_conf_file__: bool = True
    __conf_file__: Path | None = Path("./cfg/config.cfg")
    __default_prefix__ = "DAS_"

    model_config = SettingsConfigDict(
        env_prefix=__default_prefix__,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_assignment=True,
    )

    @classmethod
    def __str__(cls) -> str:
        """Nombre de la configuración en minúsculas y sin 'settings' al final."""
        name = cls.__name__.lower()
        if name.endswith("settings"):
            name = name.replace("settings", "")
        return name

    @classmethod
    def cfg_source(cls) -> dict:
        """Load config file if requires."""
        if not cls.__use_conf_file__:
            return {}
        return load_cfg_file(cls.__conf_file__) if cls.__conf_file__ else {}

    @classmethod
    def settings_customise_sources(  # pyrefly: ignore[bad-override]
        cls: type,
        settings_cls: PydanticBaseSettingsSource,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple:
        """Settings custom source."""
        return (
            init_settings,
            cls.cfg_source,  # pyrefly: ignore[missing-attribute]
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    @property
    def conf_file(self) -> Path | None:
        """Obtener el path de configuración."""
        return self.__conf_file__

    @conf_file.setter
    def conf_file(self, value: str | Path | None) -> None:
        """Establecer el archivo de configuración."""
        if value is None:
            self.__conf_file__ = None
            self.__use_conf_file__ = False
            return
        self.__conf_file__ = Path(value)
        self.__use_conf_file__ = True

    def reload_cfg(self) -> None:
        """Forzar recarga del archivo de configuración y actualizar los campos."""
        if not self.__use_conf_file__ or not self.__conf_file__:
            return

        # Carga el dict desde CFG
        cfg_data = load_cfg_file(self.__conf_file__)

        # Actualiza solo los atributos que existan en el modelo
        for key, value in cfg_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
