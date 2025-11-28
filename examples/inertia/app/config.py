import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ROOT_PATH: Path = Path(os.path.abspath(""))
    APP_PATH: Path = Path(os.path.abspath("app"))

    RESOURCES_PATH: Path = APP_PATH / "resources"
    VIEWS_PATH: Path = RESOURCES_PATH / "views"
    STATIC_PATH: Path = ROOT_PATH / "public" / "build"

    SESSION_SECRET_KEY: str = "secretkey"

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings: Settings = Settings()
