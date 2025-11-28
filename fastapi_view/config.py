import os
from starlette.templating import Jinja2Templates
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class ViewSettings(BaseSettings):
    TEMPLATES_PATH: str

    @property
    def templates(self) -> Jinja2Templates:
        return Jinja2Templates(directory=Path(self.TEMPLATES_PATH))

    model_config = SettingsConfigDict(
        env_prefix="FV_",
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
