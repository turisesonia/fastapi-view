from contextvars import ContextVar

view_request: ContextVar = ContextVar("view_request", default=None)

from .view import view, view_setup
from .inertia import inertia, setup_inertia_app
