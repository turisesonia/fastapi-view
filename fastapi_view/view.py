from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from . import view_request
from .middlewares.view_request import ViewRequestMiddleware


class View:
    _templates: Jinja2Templates = None

    @property
    def templates(self):
        return self._templates

    def setup(self, app: FastAPI, directory, handle_middleware: bool = True) -> None:
        self._handle_templates(directory)

        if handle_middleware:
            self._handle_middleware(app)

    def _handle_templates(self, directory) -> None:
        if isinstance(directory, str):
            directory = Path(directory)

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        self._templates = Jinja2Templates(directory=directory)

    def _handle_middleware(self, app: FastAPI) -> None:
        app.add_middleware(ViewRequestMiddleware)

    def __call__(self, view: str, context: dict = None, **kwargs) -> Response:
        if not self.templates or not isinstance(self.templates, Jinja2Templates):
            raise ValueError("Jinja2Templates instance is not set")

        request = view_request.get()
        if not request or not isinstance(request, Request):
            raise ValueError("request instance type must be fastapi.Request")

        if not view.endswith(".html"):
            view = f"{view}.html"

        return self.templates.TemplateResponse(
            request=request, name=view, context=context, **kwargs
        )


view = View()
