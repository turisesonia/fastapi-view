import json
import typing as t

from fastapi import Request
from fastapi.responses import JSONResponse, Response
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


class inertia:
    _instance: "inertia" = None

    _root_template: str = "app"

    _share: dict = {}

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance

        cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        self.config = InertiaConfig()

    @classmethod
    def render(cls, component: str, props: dict = {}) -> Response:
        self = cls()

        request: Request = view_request.get()

        page = self._get_page_object(component, request, props)

        if "X-Inertia" in request.headers:
            return JSONResponse(
                content=page, headers={"X-Inertia": "True", "Vary": "Accept"}
            )

        return view(self._root_template, {"page": json.dumps(page)})

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

        return self.config.assets_version

    def _get_page_object(
        self, component: str, request: Request, props: dict = {}
    ) -> dict:
        props = {**self._share, **props}

        partials = request.headers.getlist("X-Inertia-Partial-Data")
        if partials and component == request.headers.get("X-Inertia-Partial-Component"):
            props = {key: value for key, value in props.items() if key in partials}

        return {
            "version": self.get_assets_version(),
            "component": component,
            "props": props,
            "url": str(request.url),
        }
