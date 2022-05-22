from contextvars import ContextVar

view_request: ContextVar = ContextVar("view_request", default=None)

from .view import _View

view = _View()

from .inertia import _Inertia

inertia = _Inertia()