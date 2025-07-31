import typing
from pathlib import Path

from fastapi import Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask


class View:
    def __init__(self, templates: Jinja2Templates, request: Request):
        if not isinstance(templates, Jinja2Templates):
            raise TypeError("templates must be an instance of Jinja2Templates")

        if not isinstance(request, Request):
            raise ValueError("request instance type must be fastapi.Request")

        self.templates = templates
        self.request = request

    def render(
        self,
        view: str,
        context: dict | None = None,
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> Response:
        if not view.endswith(".html"):
            view = f"{view}.html"

        return self.templates.TemplateResponse(
            request=self.request,
            name=view,
            context=context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )


def view_factory(templates: str | Path | Jinja2Templates):
    if not isinstance(templates, Jinja2Templates):
        templates = Jinja2Templates(directory=templates)

    def _dependency(request: Request) -> View:
        return View(templates=templates, request=request)

    return _dependency
