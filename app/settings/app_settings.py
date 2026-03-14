import sys
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.settings.app_version import __version__
from app.settings.env_file_path import get_env_paths

class Settings(BaseSettings):
    # Datos base
    APP_NAME: str = "GenreEditor"
    APP_VERSION: str = __version__
    TIMEZONE: str = "America/Caracas"

    # ------------ Directorios ------------
    BASE_PATH: Path = Path.home() / f".{APP_NAME.lower()}"
    LOGS_PATH: Path = BASE_PATH / "logs"
    CONFIG_PATH: Path = BASE_PATH / "config"
    DATA_PATH: Path = BASE_PATH / "data"


    # ------------ Jellyfin ------------
    API_KEY: str = ""
    JELLIFYIN_HOST: str = ""
    SERVER_TIME_RESPONSE: int = 15
    LOG_LEVEL: str = "INFO"
    @field_validator("JELLIFYIN_HOST")
    @classmethod
    def clean_host_url(cls, v: str) -> str:
        return v.rstrip("/")

    model_config = SettingsConfigDict(
        env_file=get_env_paths(), 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def ensure_dirs(self) -> None:
        """
        Crea los directorios si no existen.
        """
        dirs = [self.LOGS_PATH, self.CONFIG_PATH, self.DATA_PATH]
        for dir in dirs:
            try:
                dir.mkdir(parents=True, exist_ok=True)
            except FileExistsError:
                pass
            except OSError:
                print(f" ERROR CRÍTICO: No se pudo crear el directorio {dir}. revise permisos.")
                sys.exit(1)

settings = Settings()