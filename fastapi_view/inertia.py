import hashlib
from pathlib import Path
from typing import Any

import ujson
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from fastapi_view import view_request
from fastapi_view.view import directory, view

_root_template: str = "app"

_share_data: dict = {}


def set_root_template(name: str):
    global _root_template

    _root_template = name


def share(key: str, value: Any):
    global _share_data

    _share_data[key] = value


def render(component: str, props: dict = {}) -> Jinja2Templates.TemplateResponse:
    global _root_template, _share_data

    request = view_request.get()
    props = {**_share_data, **props}

    partials = request.headers.getlist("X-Inertia-Partial-Data")
    if partials and component == request.headers.get("X-Inertia-Partial-Component"):
        props = {key: value for key, value in props.items() if key in partials}

    page = {
        "version": _get_inertia_version(),
        "component": component,
        "props": props,
        "url": str(request.url),
    }

    if "X-Inertia" in request.headers:
        return JSONResponse(
            content=page, headers={"X-Inertia": "True", "Vary": "Accept"}
        )

    context = {"page": ujson.dumps(page)}

    return view(_root_template, context)


def _get_inertia_version() -> str:
    global _root_template

    root_template_file = (
        _root_template if _root_template.endswith(".html") else f"{_root_template}.html"
    )

    path = Path(directory(), root_template_file)

    if not path.exists():
        raise FileNotFoundError(f"Inertia root template not found: {path}")

    with open(path, "rb") as tf:
        bytes_content = tf.read()

    return hashlib.sha256(bytes_content).hexdigest()
