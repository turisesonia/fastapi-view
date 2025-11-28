import json
import typing as t

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response

from ..view import ViewContext
from ..vite.extension import ViteExtension
from .config import InertiaSettings
from .enums import InertiaHeader
from .props import IgnoreFirstLoad, OptionalProp


class Inertia:
    _view: ViewContext

    _component: str | None = None

    _share: dict = {}

    def __init__(self, request: Request):
        self._view = ViewContext(request)

        self._settings = InertiaSettings()

    @classmethod
    def share(cls, key: str, value: t.Any):
        cls._share[key] = value

    @staticmethod
    def optional(prop: t.Any):
        return OptionalProp(prop)

    @property
    def _root_template(self) -> str:
        return self._settings.root_template

    @property
    def _assets_version(self) -> str | None:
        return self._settings.assets_version

    @property
    def _request(self) -> Request:
        return self._view._request

    @property
    def _is_partial_request(self) -> bool:
        return (
            InertiaHeader.PARTIAL_ONLY in self._request.headers
            and self._component
            == self._request.headers.get(InertiaHeader.PARTIAL_COMPONENT)
        )

    @property
    def _partial_only_keys(self) -> list[str]:
        keys = self._request.headers.get(InertiaHeader.PARTIAL_ONLY, "").split(",")

        return list(map(lambda s: s.strip(), keys))

    @property
    def _partial_except_keys(self) -> list[str]:
        keys = self._request.headers.get(InertiaHeader.PARTIAL_EXCEPT, "").split(",")

        return list(map(lambda s: s.strip(), keys))

    def _build_page_data(self, props: dict) -> dict:
        props = self._resolve_partial_props(props)
        props = self._resolve_callable_props(props)

        return jsonable_encoder(
            {
                "version": self._assets_version,
                "component": self._component,
                "props": {**self._share, **props},
                "url": str(self._request.url),
            }
        )

    def _resolve_partial_props(self, props: dict) -> dict[str, t.Any]:
        if not self._is_partial_request:
            return {
                key: value
                for key, value in props.items()
                if not isinstance(value, IgnoreFirstLoad)
            }

        props_ = {}
        for key, value in props.items():
            if key not in self._partial_only_keys:
                continue

            if key in self._partial_except_keys:
                continue

            props_[key] = value

        return props_

    def _resolve_callable_props(self, props: dict) -> dict:
        for key, value in props.items():
            if callable(value):
                props[key] = value()
            elif isinstance(value, dict):
                props[key] = self._resolve_callable_props(value)

        return props

    def render(self, component: str, props: dict | None = None) -> Response:
        self._component = component

        page_data = self._build_page_data(props or {})

        if InertiaHeader.INERTIA in self._request.headers:
            return JSONResponse(
                content=page_data,
                headers={
                    InertiaHeader.INERTIA: "True",
                    "Vary": "Accept",
                },
            )

        return self._view.render(self._root_template, {"page": json.dumps(page_data)})


def get_inertia_context(request: Request):
    inertia = Inertia(request)

    inertia._view._templates.env.add_extension(ViteExtension)

    return inertia
