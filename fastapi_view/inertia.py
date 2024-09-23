import json
import typing as t
from typing import Any

from fastapi import Request
from fastapi.responses import Response, JSONResponse
from fastapi.templating import Jinja2Templates

from fastapi_view import view_request
from fastapi_view.view import view


class InertiaLoader:
    _instance: "InertiaLoader" = None

    _root_template: str = "app"

    _share: dict = {}

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance

        cls._instance = super().__new__(cls)

        return cls._instance

    def set_root_template(self, root_template: str):
        self._root_template = root_template

    def share(self, key: str, value: t.Any):
        self._share[key] = value

    def get_page_object(
        self, component: str, request: Request, props: dict = {}
    ) -> dict:
        props = {**self._share, **props}

        partials = request.headers.getlist("X-Inertia-Partial-Data")
        if partials and component == request.headers.get("X-Inertia-Partial-Component"):
            props = {key: value for key, value in props.items() if key in partials}

        return {
            "version": self._get_assets_version(),
            "component": component,
            "props": props,
            "url": str(request.url),
        }

    def _get_assets_version(self) -> str:
        return ""


def set_root_template(root_template: str):
    InertiaLoader().set_root_template(root_template)


def share(key: str, value: Any):
    InertiaLoader().share(key, value)


def render(component: str, props: dict = {}) -> Response:
    instance = InertiaLoader()
    request: Request = view_request.get()

    page = instance.get_page_object(component, request, props)

    if "X-Inertia" in request.headers:
        return JSONResponse(
            content=page, headers={"X-Inertia": "True", "Vary": "Accept"}
        )

    return view(instance._root_template, {"page": json.dumps(page)})
