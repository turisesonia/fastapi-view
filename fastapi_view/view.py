from pathlib import Path

from fastapi import Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from . import view_request
from .vite import Vite


class ViewLoader:
    _instance: "ViewLoader" = None

    _directory: str | Path = None

    _templates: Jinja2Templates | None = None

    def __new__(cls):
        """Singleton pattern"""

        if cls._instance is not None:
            return cls._instance

        cls._instance = super().__new__(cls)

        return cls._instance

    @classmethod
    def set_templates(cls, templates: Jinja2Templates):
        if not isinstance(templates, Jinja2Templates):
            raise ValueError(
                "templates instance type must be fastapi.templating.Jinja2Templates"
            )

        cls()._templates = templates


def init_fastapi_view(templates: Jinja2Templates):
    ViewLoader.set_templates(templates)


def view(view: str, context: dict, **kwargs) -> Response:
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
