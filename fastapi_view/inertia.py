import json
import typing as t
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from fastapi_view import view_request
from fastapi_view.config import inertia_config
from fastapi_view.enums import Header
from fastapi_view.middlewares.inertia_request import InertiaRequestMiddleware
from fastapi_view.view import view
from fastapi_view.vite import Vite


class InertiaPageProps(BaseModel):
    data: t.Any = {}


class LazyProp:
    def __init__(self, prop: t.Any):
        self._prop = prop

    def __call__(self):
        return self._prop() if callable(self._prop) else self._prop


class _Inertia:
    _root_template: str = None

    _share: dict = {}

    @property
    def root_template(self) -> str:
        return self._root_template

    def setup(
        self,
        app: FastAPI,
        directory: t.Union[str, Path, Path],
        root_template: str = "app.html",
        use_vite: bool = False,
    ):
        if not view.templates:
            view.setup(app, directory, handle_middleware=False)

        self._handle_root_template(root_template)
        self._handle_middleware(app)

        if use_vite:
            self._handle_vite(app)

    def _handle_root_template(self, root_template: str):
        self._root_template = root_template

    def _handle_middleware(self, app: FastAPI):
        app.add_middleware(InertiaRequestMiddleware)

    def _handle_vite(self, app: FastAPI):
        Vite(app=app, templates=view.templates)

    def __call__(self, component: str, props: dict = None) -> Response:
        request: Request = view_request.get()

        page_props = self._build_page_props(component, request, props or {})

        if "X-Inertia" in request.headers:
            return JSONResponse(
                content=page_props, headers={"X-Inertia": "True", "Vary": "Accept"}
            )

        return view(self._root_template, {"page": json.dumps(page_props)})

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
                    "version": inertia_config.assets_version,
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

    def share(self, key: str, value: t.Any):
        self._share[key] = value

    @staticmethod
    def lazy(prop: t.Any):
        return LazyProp(prop)


inertia = _Inertia()


# class inertia__:
#     _instance: "inertia" = None

#     _root_template: str = "app"

#     _share: dict = {}

#     def __new__(cls):
#         if cls._instance is not None:
#             return cls._instance

#         cls._instance = super().__new__(cls)

#         return cls._instance

#     @classmethod
#     def render(cls, component: str, props: dict = None) -> Response:
#         self = cls()

#         request: Request = view_request.get()

#         page_props = self._build_page_props(component, request, props or {})

#         if "X-Inertia" in request.headers:
#             return JSONResponse(
#                 content=page_props, headers={"X-Inertia": "True", "Vary": "Accept"}
#             )

#         return view(self._root_template, {"page": json.dumps(page_props)})

#     @classmethod
#     def set_root_template(cls, root_template: str):
#         self = cls()

#         self._root_template = root_template

#     @classmethod
#     def share(cls, key: str, value: t.Any):
#         self = cls()

#         self._share[key] = value

#     @staticmethod
#     def lazy(prop: t.Any):
#         return LazyProp(prop)

#     def _build_page_props(self, component: str, request: Request, props: dict) -> dict:
#         is_partial_request = self._is_parital_request(component, request)

#         partials = list(
#             map(
#                 lambda s: s.strip(),
#                 request.headers.get(Header.X_INERTIA_PARTIAL_DATA, "").split(","),
#             )
#         )

#         for key in list(props.keys()):
#             if is_partial_request:
#                 if key not in partials:
#                     del props[key]
#             else:
#                 if isinstance(props[key], LazyProp):
#                     del props[key]

#         props = self._deep_resolve_callable_props(props)

#         return (
#             InertiaPageProps(
#                 data={
#                     "version": inertia_config.assets_version,
#                     "component": component,
#                     "props": {**self._share, **props},
#                     "url": str(request.url),
#                 }
#             )
#             .model_dump(mode="json")
#             .get("data", {})
#         )

#     def _is_parital_request(self, component: str, request: Request) -> bool:
#         return (
#             component == request.headers.get(Header.X_INERTIA_PARTIAL_COMPONENT)
#             and Header.X_INERTIA_PARTIAL_DATA in request.headers
#         )

#     def _deep_resolve_callable_props(self, props: dict) -> dict:
#         for key, value in props.items():
#             if callable(value):
#                 props[key] = value()

#             elif isinstance(value, dict):
#                 props[key] = self._deep_resolve_callable_props(value)

#             else:
#                 ...

#         return props


# def setup_inertia_app(
#     app: FastAPI,
#     root_template: str = "app",
#     templates: Jinja2Templates = None,
#     use_vite: bool = False,
# ) -> FastAPI:
#     if not view._templates:
#         if not templates:
#             raise ValueError("Jinja2Templates is not set")

#         if templates and not isinstance(templates, Jinja2Templates):
#             raise ValueError(
#                 "templates object type must be fastapi.templating.Jinja2Templates"
#             )

#         view.initialize(templates=templates)

#     inertia.set_root_template(root_template)

#     app.add_middleware(InertiaRequestMiddleware)

#     if use_vite:
#         vite = Vite(templates=view.get_templates())

#     return app
