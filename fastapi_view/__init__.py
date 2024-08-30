from contextvars import ContextVar

view_request: ContextVar = ContextVar("view_request", default=None)

from .view import init_jinja2_templates, view
from .vite import _Vite

vite = _Vite()
