import json
import typing as t

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response

from ..view import ViewContext
from ..vite.extension import ViteExtension
from .config import InertiaSettings
from .enums import InertiaHeader
from .props import CallableProp, DeferredProp, IgnoreFirstLoad, MergeProp, OptionalProp

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
    mergeProps: list[str]
    prependProps: list[str]
    deepMergeProps: list[str]
    matchPropsOn: dict[str, str]


class InertiaShare:
    def __init__(self):
        self._share: dict = {}

    def share(self, key: str, value: t.Any):
        self._share[key] = value


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

    @staticmethod
    def merge(prop: t.Any) -> MergeProp:
        """
        Create a mergeable property that combines with existing data.

        Args:
            prop: Callable or value to merge

        Returns:
            MergeProp instance

        Example:
            # Basic merge (appends to root array)
            Inertia.merge(lambda: get_more_posts())

            # Prepend instead of append
            Inertia.merge(lambda: get_new_posts()).prepend()

            # Merge specific nested path
            Inertia.merge(lambda: get_users()).append('data')

            # Match on ID to update existing items
            Inertia.merge(lambda: get_users()).append('data', match_on='id')
        """

        return MergeProp(prop)

    @staticmethod
    def deep_merge(prop: t.Any) -> MergeProp:
        """
        Create a deep mergeable property that recursively combines with existing data.

        Args:
            prop: Callable or value to deep merge

        Returns:
            MergeProp instance configured for deep merging

        Example:
            Inertia.deep_merge(lambda: get_settings())
        """

        return MergeProp(prop).deep_merge()


class Inertia(InertiaShare, InertiaProp):
    _view: ViewContext

    _component: str | None = None

    def __init__(self, request: Request):
        super().__init__()

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
        # Resolve metadata configurations (only for initial loads)
        deferred_props = self._resolve_deferred_props(props)
        merge_props = self._resolve_merge_props(props)

        # Get flash messages
        flash_props = self._get_flash_props()

        # Resolve all props
        resolved_props = self._resolve_props(props)

        # Build base page object
        page_object = PageObject(
            component=self._component,
            props={**self._share, **flash_props, **resolved_props},
            url=str(self._request.url),
            version=self._assets_version,
        )

        # Add metadata ONLY for initial loads
        if deferred_props:
            page_object["deferredProps"] = deferred_props

        if merge_props:
            # Spread merge config keys into page object
            page_object.update(merge_props)

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

    def _resolve_merge_props(self, props: dict) -> dict[str, list[str] | dict] | None:
        """
        Build merge configuration metadata for client.

        Returns dictionary with merge instructions:
        {
            "mergeProps": ["users", "posts"],
            "prependProps": ["notifications"],
            "deepMergeProps": ["settings"],
            "matchPropsOn": {"users": "id", "posts": "id"}
        }

        Returns metadata for both initial and partial requests.
        The client needs this metadata on every response to know how to merge props.
        """
        merge_config = {}
        merge_props = []
        prepend_props = []
        deep_merge_props = []
        match_props_on = {}

        for key, value in props.items():
            if not isinstance(value, MergeProp):
                continue

            # Collect merge props
            if value.should_merge():
                merge_props.append(key)

            # Collect prepend props
            if value.prepends_at_root():
                prepend_props.append(key)

            # Collect deep merge props
            if value.should_deep_merge():
                deep_merge_props.append(key)

            # Collect match strategies
            match_fields = value.matches_on()
            if match_fields:
                # Use first match field (Laravel behavior)
                match_props_on[key] = match_fields[0]

        # Only include non-empty arrays
        if merge_props:
            merge_config["mergeProps"] = merge_props
        if prepend_props:
            merge_config["prependProps"] = prepend_props
        if deep_merge_props:
            merge_config["deepMergeProps"] = deep_merge_props
        if match_props_on:
            merge_config["matchPropsOn"] = match_props_on

        return merge_config if merge_config else None

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
            return {FLASH_PROPS_KEY: {}}

        props = session.pop(FLASH_PROPS_KEY, {})

        return {FLASH_PROPS_KEY: props}


def get_inertia_context(request: Request):
    inertia = Inertia(request)

    inertia._view._templates.env.add_extension(ViteExtension)

    return inertia
