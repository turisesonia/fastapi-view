import json
import typing as t

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from fastapi_view import view_request
from fastapi_view.enums import Header
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


class LazyProp:
    def __init__(self, prop: t.Any):
        self._prop = prop

    def __call__(self):
        return self._prop() if callable(self._prop) else self._prop


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

        page_props = self._build_page_props(component, request, props or {})

        if "X-Inertia" in request.headers:
            return JSONResponse(
                content=page_props, headers={"X-Inertia": "True", "Vary": "Accept"}
            )

        return view(self._root_template, {"page": json.dumps(page_props)})

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

    @staticmethod
    def lazy(prop: t.Any):
        return LazyProp(prop)

    def _build_page_props(self, component: str, request: Request, props: dict) -> dict:
        is_partial_request = self._is_parital_request(component, request)

        partials = list(
            map(
                lambda s: s.strip(),
                request.headers.get(Header.X_INERTIA_PARTIAL_DATA, "").split(","),
            )
        )

        for key in list(props.keys()):
            if is_partial_request:
                if key not in partials:
                    del props[key]
            else:
                if isinstance(props[key], LazyProp):
                    del props[key]

        props = self._deep_resolve_callable_props(props)

        return (
            InertiaPageProps(
                data={
                    "version": self.get_assets_version(),
                    "component": component,
                    "props": {**self._share, **props},
                    "url": str(request.url),
                }
            )
            .model_dump(mode="json")
            .get("data", {})
        )

    def _is_parital_request(self, component: str, request: Request) -> bool:
        return (
            component == request.headers.get(Header.X_INERTIA_PARTIAL_COMPONENT)
            and Header.X_INERTIA_PARTIAL_DATA in request.headers
        )

    def _deep_resolve_callable_props(self, props: dict) -> dict:
        for key, value in props.items():
            if callable(value):
                props[key] = value()

            elif isinstance(value, dict):
                props[key] = self._deep_resolve_callable_props(value)

            else:
                ...

        return props
