import os
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ViteSettings(BaseSettings):
    dev_mode: bool = False
    dev_server_protocol: str = "http"
    dev_server_host: str = "localhost"
    dev_server_port: int = 5173
    ws_client_path: str = "@vite/client"
    manifest_path: str | Path = "dist/.vite/manifest.json"
    dist_path: Path = Path("dist")
    dist_uri_prefix: str | None = None
    static_url: str | None = None

    @field_validator("dist_uri_prefix")
    @classmethod
    def validate_dist_uri_prefix(cls, v: str | None) -> str | None:
        if v is not None and not v:
            raise ValueError("dist_uri_prefix must be a non-empty string")

        return v

    @model_validator(mode="after")
    def validate_production_config(self) -> "ViteSettings":
        if not self.dev_mode:
            if not self.static_url and not self.dist_uri_prefix:
                raise ValueError(
                    "static_url or dist_uri_prefix must be set in production mode"
                )

        return self

    @property
    def dev_server_url(self) -> str:
        return f"{self.dev_server_protocol}://{self.dev_server_host}:{self.dev_server_port}"

    @property
    def dev_websocket_url(self) -> str:
        return f"{self.dev_server_url}/{self.ws_client_path}"

    model_config = SettingsConfigDict(
        env_prefix="FV_VITE_",
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
