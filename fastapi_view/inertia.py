import json
import typing as t

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from fastapi_view import view_request
from fastapi_view.view import view


class InertiaConfig(BaseSettings):
    assets_version: str = ""

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="INERTIA_",
    )


class InertiaPageProps(BaseModel):
    data: t.Any = {}


class inertia:
    _instance: "inertia" = None

    _config: InertiaConfig = None

    _root_template: str = "app"

    _share: dict = {}

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance

        cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if not self._config:
            self._config = InertiaConfig()

    @classmethod
    def render(cls, component: str, props: dict = None) -> Response:
        self = cls()

        request: Request = view_request.get()

        page_props = self._get_page_props(component, request, props or {})

        data = page_props.model_dump(mode="json").get("data", {})

        if "X-Inertia" in request.headers:
            return JSONResponse(
                content=data, headers={"X-Inertia": "True", "Vary": "Accept"}
            )

        return view(self._root_template, {"page": json.dumps(data)})

    @classmethod
    def set_root_template(cls, root_template: str):
        self = cls()

        self._root_template = root_template

    @classmethod
    def share(cls, key: str, value: t.Any):
        self = cls()

        self._share[key] = value

    @classmethod
    def get_assets_version(cls) -> str:
        self = cls()

        return self._config.assets_version

    def _get_page_props(
        self, component: str, request: Request, props: dict
    ) -> InertiaPageProps:
        partials = request.headers.getlist("X-Inertia-Partial-Data")

        if partials and component == request.headers.get("X-Inertia-Partial-Component"):
            props = {key: value for key, value in props.items() if key in partials}

        return InertiaPageProps(
            data={
                "version": self.get_assets_version(),
                "component": component,
                "props": {**self._share, **props},
                "url": str(request.url),
            }
        )
