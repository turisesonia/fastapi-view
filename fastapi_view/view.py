from fastapi import Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask

from fastapi_view.config import ViewSettings


class ViewContext:
    _request: Request
    _templates: Jinja2Templates

    def __init__(self, request: Request):
        if not isinstance(request, Request):
            raise ValueError("request instance type must be fastapi.Request")

        self._request = request
        self._templates = ViewSettings().templates

    def render(
        self,
        view: str,
        context: dict | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> Response:
        if not view.endswith(".html"):
            view = f"{view}.html"

        return self._templates.TemplateResponse(
            request=self._request,
            name=view,
            context=context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )


def get_view_context(request: Request):
    return ViewContext(request=request)
