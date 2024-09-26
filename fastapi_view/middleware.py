from fastapi import Request
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from . import view_request
from .inertia import inertia


class ViewRequestMiddleware:
    def __init__(self, app: ASGIApp, use_inertia: bool = False) -> None:
        self.app = app

        self.use_inertia = use_inertia

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive, send)

        if self.inertia_is_outdated(request):
            response = PlainTextResponse(
                "", status_code=409, headers={"X-Inertia-Location": str(request.url)}
            )
            await response(scope, receive, send)
            return

        try:
            token = view_request.set(request)

            await self.app(scope, receive, send)

        finally:
            view_request.reset(token)

    def inertia_is_outdated(self, request: Request) -> bool:
        assets_version = inertia.get_assets_version()

        # Check if the asset version is the same as the one in the request.
        if (
            self.use_inertia
            and request.headers.get("X-Inertia-Version", assets_version)
            != assets_version
        ):
            return True

        return False
