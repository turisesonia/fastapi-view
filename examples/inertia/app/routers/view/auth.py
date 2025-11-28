from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi_view.inertia import InertiaDepends

from app.data import USERS
from app.schemas.auth import LoginRequest

router = APIRouter(tags=["auth"])


@router.get("/login")
def login_page(request: Request, inertia: InertiaDepends):
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=303)

    return inertia.render("Auth/Login")


@router.post("/login")
def login(request: Request, inertia: InertiaDepends, body: LoginRequest):
    user = next(
        (u for u in USERS.values() if u["email"] == body.email and u["password"] == body.password),
        None,
    )

    if not user:
        return inertia.back(
            errors={"email": "These credentials do not match our records."}
        )

    request.session["user_id"] = user["id"]

    return RedirectResponse(url="/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()

    return RedirectResponse(url="/login", status_code=303)
