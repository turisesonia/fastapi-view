import json
import typing as t

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response

from fastapi_view.inertia.props import DeferredProp

from ..view import ViewContext
from ..vite.extension import ViteExtension
from .config import InertiaSettings
from .enums import InertiaHeader
from .props import CallableProp, IgnoreFirstLoad, OptionalProp

REQUEST_SESSION_KEY: str = "session"
FLASH_PROPS_KEY: str = "flash"


class PageObject(t.TypedDict, total=False):
    component: str
    props: dict
    url: str
    version: str | None
    clearHistory: bool
    encryptHistory: bool
    deferredProps: dict[str, list[str]]


class InertiaShare:
    _share: dict = {}

    @classmethod
    def share(cls, key: str, value: t.Any):
        cls._share[key] = value


class InertiaProp:
    @staticmethod
    def optional(prop: t.Any):
        return OptionalProp(prop)

    @staticmethod
    def defer(prop: t.Any, group: str = "default") -> DeferredProp:
        """
        Create a deferred property that loads after initial page render.

        Args:
            prop: Callable or value to defer
            group: Group name for batching related deferred props

        Returns:
            DeferredProp instance

        Example:
            Inertia.defer(lambda: get_posts(), group='content')
        """

        return DeferredProp(prop, group)


class Inertia(InertiaShare, InertiaProp):
    _view: ViewContext

    _component: str | None = None

    def __init__(self, request: Request):
        self._view = ViewContext(request)
        self._settings = InertiaSettings()

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

    def render(self, component: str, props: dict | None = None) -> Response:
        self._component = component

        page_object = self._build_page_object(props or {})

        if InertiaHeader.INERTIA in self._request.headers:
            return JSONResponse(
                content=page_object,
                headers={
                    InertiaHeader.INERTIA: "True",
                    "Vary": "Accept",
                },
            )

        return self._view.render(self._root_template, {"page": json.dumps(page_object)})

    def _build_page_object(self, props: dict) -> dict:
        deferred_props = self._resolve_deferred_props(props)
        flash_props = self._get_flash_props()

        props = self._resolve_props(props)

        # Build base page object
        page_object = PageObject(
            component=self._component,
            props={**self._share, **flash_props, **props},
            url=str(self._request.url),
            version=self._assets_version,
        )

        # Add deferredProps config ONLY for initial loads
        if deferred_props:
            page_object["deferredProps"] = deferred_props

        return jsonable_encoder(page_object)

    def _resolve_deferred_props(self, props: dict) -> dict | None:
        if self._is_partial_request:
            return None

        deferred_props = {}
        for key, value in props.items():
            if not isinstance(value, DeferredProp):
                continue

            group = value.group
            if group not in deferred_props:
                deferred_props[group] = []

            deferred_props[group].append(key)

        return deferred_props

    def _resolve_props(self, props: dict) -> dict:
        props = self._resolve_partial_props(props)
        props = self._resolve_property_instances(props)

        return props

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

    def _resolve_property_instances(self, props: dict) -> dict:
        """
        Resolve special property instances (CallableProp, DeferredProp, etc.)

        This is equivalent to Laravel's resolvePropertyInstances() method.
        It executes callables for props that survived the filtering stage.
        """
        resolved = {}

        for key, value in props.items():
            if isinstance(value, CallableProp):
                resolved[key] = value()

            elif callable(value):
                resolved[key] = value()

            elif isinstance(value, dict):
                resolved[key] = self._resolve_property_instances(value)

            else:
                resolved[key] = value

        return resolved

    def flash(self, key: str, value: t.Any):
        session = self._get_request_session()

        if session is None:
            raise RuntimeError(
                "SessionMiddleware must be installed to use flash messages."
            )

        if FLASH_PROPS_KEY not in session:
            session[FLASH_PROPS_KEY] = {}

        session[FLASH_PROPS_KEY][key] = value

    def _get_request_session(self):
        if REQUEST_SESSION_KEY not in self._request.scope:
            return None

        return self._request.session

    def _get_flash_props(self) -> dict:
        session = self._get_request_session()
        if session is None:
            return {FLASH_PROPS_KEY: None}

        props = session.pop(FLASH_PROPS_KEY, {})

        return {FLASH_PROPS_KEY: props}


def get_inertia_context(request: Request):
    inertia = Inertia(request)

    inertia._view._templates.env.add_extension(ViteExtension)

    return inertia
