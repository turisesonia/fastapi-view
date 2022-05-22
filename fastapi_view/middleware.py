from starlette.types import ASGIApp, Receive, Scope, Send
from fastapi import Request

from . import view_request


class ViewRequestMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive, send)

        try:
            token = view_request.set(request)
            await self.app(scope, receive, send)

        finally:
            view_request.reset(token)
