import ujson
import hashlib
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from . import view


class _Inertia(object):
    def __init__(self):
        self._root_template = "app"
        self._share_data = {}

    @property
    def root_template(self):
        """The root_template property."""
        return self._root_template

    @root_template.setter
    def root_template(self, root_template: str):
        self._root_template = root_template

    @property
    def share_data(self):
        """The share_data property."""
        return self._share_data

    @share_data.setter
    def share_data(self, share_data: dict):
        self._share_data = share_data

    def share(self, key: str, value: Any):
        self._share_data[key] = value

    def get_inertia_version(self):
        root_template_file = (
            self.root_template
            if self.root_template.endswith(".html")
            else f"{self.root_template}.html"
        )

        with open(f"{view.views_directory}/{root_template_file}", "rb") as tf:
            bytes_content = tf.read()

        return hashlib.sha256(bytes_content).hexdigest()

    def render(self, component: str, request: Request, props: dict = {}):
        props = {**self.share_data, **props}

        partial_props = request.headers.getlist("X-Inertia-Partial-Data")

        if partial_props and component == request.headers.get(
            "X-Inertia-Partial-Component"
        ):
            props = {key: value for key, value in props.items() if key in partial_props}

        page = {
            "version": self.get_inertia_version(),
            "component": component,
            "props": props,
            "url": str(request.url),
        }

        if "X-Inertia" in request.headers:
            return JSONResponse(
                content=page, headers={"X-Inertia": "True", "Vary": "Accept"}
            )

        context = {
            "request": request,
            "page": ujson.dumps(page),
        }

        return view(self.root_template, context)
