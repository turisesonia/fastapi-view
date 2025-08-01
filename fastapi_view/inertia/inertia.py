import json
import typing as t
from pathlib import Path

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi.templating import Jinja2Templates

from fastapi_view.config import ViteConfig
from fastapi_view.inertia.enums import InertiaHeader
from fastapi_view.inertia.vite import Vite
from fastapi_view.view import View


class LazyProp:
    def __init__(self, prop: t.Any):
        self._prop = prop

    def __call__(self):
        return self._prop() if callable(self._prop) else self._prop


class Inertia:
    _share: dict = {}

    def __init__(self, view: View, root_template: str, assets_version: str = ""):
        self.view = view
        self.root_template = root_template
        self.assets_version = assets_version

    def render(self, component: str, props: dict | None = None) -> Response:
        request = self.view.request

        page_props = self._build_page_props(component, request, props or {})

        if InertiaHeader.X_INERTIA in request.headers:
            return JSONResponse(
                content=page_props,
                headers={
                    InertiaHeader.X_INERTIA: "True",
                    "Vary": "Accept",
                },
            )

        return self.view.render(self.root_template, {"page": json.dumps(page_props)})

    def _build_page_props(self, component: str, request: Request, props: dict) -> dict:
        is_partial_request = (
            InertiaHeader.X_INERTIA_PARTIAL_DATA in request.headers
            and component
            == request.headers.get(InertiaHeader.X_INERTIA_PARTIAL_COMPONENT)
        )

        partial_data = request.headers.get(
            InertiaHeader.X_INERTIA_PARTIAL_DATA, ""
        ).split(",")
        partials = list(map(lambda s: s.strip(), partial_data))

        for key in list(props.keys()):
            if is_partial_request:
                if key not in partials:
                    del props[key]
            else:
                if isinstance(props[key], LazyProp):
                    del props[key]

        props = self._resolve_prop_callables(props)

        return jsonable_encoder(
            {
                "version": self.assets_version,
                "component": component,
                "props": {**self._share, **props},
                "url": str(request.url),
            }
        )

    def _resolve_prop_callables(self, props: dict) -> dict:
        for key, value in props.items():
            if callable(value):
                props[key] = value()
            elif isinstance(value, dict):
                props[key] = self._resolve_prop_callables(value)

        return props

    def share(self, key: str, value: t.Any):
        self._share[key] = value

    @staticmethod
    def lazy(prop: t.Any):
        return LazyProp(prop)


def inertia_factory(
    templates: str | Path | Jinja2Templates,
    root_template: str,
    assets_version: str = "",
    vite_config: ViteConfig | None = None,
):
    if not isinstance(templates, Jinja2Templates):
        templates = Jinja2Templates(directory=templates)

    def _dependency(request: Request) -> Inertia:
        view = View(templates=templates, request=request)

        if vite_config:
            Vite(vite_config, templates)

        return Inertia(view, root_template, assets_version)

    return _dependency
