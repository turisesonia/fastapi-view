from pydantic_settings import BaseSettings, SettingsConfigDict


class InertiaConfig(BaseSettings):
    assets_version: str = ""

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="INERTIA_",
    )


inertia_config = InertiaConfig()
