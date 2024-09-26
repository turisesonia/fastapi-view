from contextvars import ContextVar

view_request: ContextVar = ContextVar("view_request", default=None)

from .view import view
from .inertia import inertia
