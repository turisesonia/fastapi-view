from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from . import view_request
from .loaders import ViewLoader


def init_jinja2_templates(directory: str | Path, **kwargs):
    ViewLoader().set_jinja2_templates(directory, **kwargs)


def directory() -> str | Path:
    return ViewLoader()._directory


def view(view: str, context: dict, **kwargs) -> Jinja2Templates.TemplateResponse:
    _templates = ViewLoader()._templates

    if not _templates:
        raise ValueError("Jinja2Templates instance is not set")

    request = view_request.get()

    if not request or not isinstance(request, Request):
        raise ValueError("request instance type must be fastapi.Request")

    if not view.endswith(".html"):
        view = f"{view}.html"

    context["request"] = request

    return _templates.TemplateResponse(name=view, context=context, **kwargs)
