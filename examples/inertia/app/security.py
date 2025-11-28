import typing as t
from fastapi import Depends, Request, HTTPException, status
from fastapi_view.inertia import InertiaDepends

from app.data import USERS


def get_current_user(request: Request, inertia: InertiaDepends) -> dict:
    user_id = request.session.get("user_id")
    user = USERS.get(user_id) if user_id else None

    user_safe = {k: v for k, v in user.items() if k != "password"} if user else None

    inertia.share("auth", {"user": user_safe})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, headers={"Location": "/login"}
        )

    return user_safe


CurrentUser = t.Annotated[dict, Depends(get_current_user)]
