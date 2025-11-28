from fastapi import APIRouter
from fastapi_view.inertia import InertiaDepends

from app.security import CurrentUser

router = APIRouter(tags=["dashboard"])


@router.get("/")
def dashboard(inertia: InertiaDepends, user: CurrentUser):
    return inertia.render("Dashboard/Index")
