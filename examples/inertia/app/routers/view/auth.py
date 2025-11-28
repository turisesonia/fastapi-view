from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi_view.inertia import InertiaDepends

from app.schemas.auth import LoginRequest
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
def login_page(request: Request, inertia: InertiaDepends):
    if request.session.get("user"):
        return RedirectResponse(url="/", status_code=303)

    return inertia.render("Auth/Login")


@router.post("/login")
def login(request: Request, inertia: InertiaDepends, body: LoginRequest):
    service = AuthService()
    user = service.authenticate(body.username, body.password)

    if not user:
        return inertia.render(
            "Auth/Login",
            {
                "error": "用戶名或密碼錯誤",
                "username": body.username,  # 保留用戶名方便重新輸入
            },
        )

    request.session["user"] = user

    return RedirectResponse(url="/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()

    return RedirectResponse(url="/auth/login", status_code=303)
