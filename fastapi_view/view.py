from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from . import view_request


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

    def set_jinja2_templates(self, directory: str | Path, **kwargs):
        self._directory = directory
        self._templates = Jinja2Templates(directory=directory, **kwargs)


def init_jinja2_templates(directory: str | Path, **kwargs):
    ViewLoader().set_jinja2_templates(directory, **kwargs)


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
