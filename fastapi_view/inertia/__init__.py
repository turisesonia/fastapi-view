from typing import Annotated

from fastapi import Depends

from .inertia import Inertia, get_inertia_context

InertiaDepends = Annotated[Inertia, Depends(get_inertia_context)]

__all__ = ["Inertia", "get_inertia_context", "InertiaDepends"]
