import typing as t

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from . import view_request
from .middlewares.view_request import ViewRequestMiddleware
from .vite import Vite


class ViewLoader:
    _vite: Vite = None

    _templates: t.Optional[Jinja2Templates] = None

    def __call__(self, view: str, context: dict = None, **kwargs) -> Response:
        templates = self.get_templates()

        if not templates:
            raise ValueError("Jinja2Templates instance is not set")

        request = view_request.get()
        if not request or not isinstance(request, Request):
            raise ValueError("request instance type must be fastapi.Request")

        if not context:
            context = {}

        context["request"] = request

        if not view.endswith(".html"):
            view = f"{view}.html"

        return templates.TemplateResponse(name=view, context=context, **kwargs)

    def initialize(self, templates: Jinja2Templates):
        self.set_templates(templates)

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


def view_setup(app: FastAPI, templates: Jinja2Templates) -> FastAPI:
    view.initialize(templates=templates)

    app.add_middleware(ViewRequestMiddleware)

    return app
