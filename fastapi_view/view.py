from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from . import view_request

_directory: str | Path = None
_templates: Jinja2Templates | None = None


def init_jinja2_templates(directory: str | Path, **kwargs):
    global _directory, _templates

    _directory = directory
    _templates = Jinja2Templates(directory=directory, **kwargs)


def directory() -> str | Path:
    global _directory

    return _directory


def view(view: str, context: dict, **kwargs) -> Jinja2Templates.TemplateResponse:
    global _template

    if not _templates:
        raise ValueError("Jinja2Templates instance is not set")

    request = view_request.get()

    if not request or not isinstance(request, Request):
        raise ValueError("request instance type must be fastapi.Request")

    if not view.endswith(".html"):
        view = f"{view}.html"

    context["request"] = request

    return _templates.TemplateResponse(name=view, context=context, **kwargs)
