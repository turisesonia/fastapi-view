from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse

from ..depends import InertiaDepend
from .schemas import LoginRequest
from .services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
def login_page(request: Request, inertia: InertiaDepend):
    if request.session.get("user"):
        return RedirectResponse(url="/", status_code=303)

    return inertia.render("Auth/Login")


@router.post("/login")
def login(
    request: Request,
    inertia: InertiaDepend,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(),
):
    user = auth_service.authenticate_user(login_data.username, login_data.password)

    if not user:
        return inertia.render(
            "Auth/Login",
            {
                "error": "用戶名或密碼錯誤",
                "username": login_data.username,  # 保留用戶名方便重新輸入
            },
        )

    request.session["user"] = user
    return RedirectResponse(url="/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()  # 清除 session
    return RedirectResponse(url="/auth/login", status_code=303)
