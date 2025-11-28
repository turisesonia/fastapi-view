import typing as t
from fastapi import Depends, Request, HTTPException, status
from fastapi_view.inertia import InertiaDepends


def get_current_user(request: Request, inertia: InertiaDepends) -> dict:
    user = request.session.get("user")

    inertia.share("auth", {"user": user})

    if not user:
        # 使用 Inertia 重定向到登入頁面
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, headers={"Location": "/auth/login"}
        )

    return user


CurrentUser = t.Annotated[dict, Depends(get_current_user)]
