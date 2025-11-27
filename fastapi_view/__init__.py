from typing import Annotated
from fastapi import Depends
from fastapi_view.view import ViewContext, get_view_context


ViewDepends = Annotated[ViewContext, Depends(get_view_context)]

__all__ = ["ViewContext", "get_view_context"]
