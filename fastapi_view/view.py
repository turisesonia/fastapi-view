from fastapi import Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from . import view_request
from .vite import Vite


class ViewLoader:
    _vite: Vite = None

    _templates: Jinja2Templates | None = None

    def __call__(self, view: str, context: dict, **kwargs) -> Response:
        templates = self.get_templates()

        if not templates:
            raise ValueError("Jinja2Templates instance is not set")

        request = view_request.get()

        if not request or not isinstance(request, Request):
            raise ValueError("request instance type must be fastapi.Request")

        context["request"] = request

        if not view.endswith(".html"):
            view = f"{view}.html"

        return templates.TemplateResponse(name=view, context=context, **kwargs)

    def initialize(self, templates: Jinja2Templates, use_vite: bool = False):
        self.set_templates(templates)

        if use_vite:
            self._vite = Vite(templates=templates)

    def set_templates(self, templates: Jinja2Templates):
        if not isinstance(templates, Jinja2Templates):
            raise ValueError(
                "templates instance type must be fastapi.templating.Jinja2Templates"
            )

        self._templates = templates

    def get_templates(self) -> Jinja2Templates:
        if not self._templates or not isinstance(self._templates, Jinja2Templates):
            raise ValueError("Jinja2Templates instance is not set")

        return self._templates


view = ViewLoader()
