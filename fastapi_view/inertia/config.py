import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class InertiaSettings(BaseSettings):
    root_template: str = "app.html"
    assets_version: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="FV_INERTIA_",
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
