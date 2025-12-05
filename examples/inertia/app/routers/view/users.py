from datetime import datetime
from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
from fastapi_view.inertia import InertiaDepends

from app.data import USERS, get_next_id
from app.schemas.user import UserCreate, UserUpdate
from app.security import CurrentUser
from typing import Annotated

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def index(
    inertia: InertiaDepends,
    user: CurrentUser,
    search: Annotated[str, Query()] = "",
    trashed: Annotated[str, Query()] = "",
):
    users = list(USERS.values())

    if search:
        users = [
            u for u in users
            if search.lower() in u["first_name"].lower() or search.lower() in u["last_name"].lower() or search.lower() in u["email"].lower()
        ]

    if trashed == "only":
        users = [u for u in users if u["deleted_at"] is not None]
    elif trashed != "with":
        users = [u for u in users if u["deleted_at"] is None]

    users_safe = [{k: v for k, v in u.items() if k != "password"} for u in users]

    return inertia.render(
        "Users/Index",
        {
            "users": users_safe,
            "filters": {"search": search, "trashed": trashed},
        },
    )


@router.get("/create")
def create(inertia: InertiaDepends, user: CurrentUser):
    return inertia.render("Users/Create")


@router.post("")
def store(
    inertia: InertiaDepends,
    user: CurrentUser,
    data: UserCreate,
):
    user_id = get_next_id("user")
    USERS[user_id] = {
        "id": user_id,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "password": data.password,
        "owner": data.owner,
        "deleted_at": None,
    }

    # Flash success message
    inertia.flash("success", f"User '{data.first_name} {data.last_name}' created successfully.")

    return RedirectResponse(url="/users", status_code=303)


@router.get("/{user_id}/edit")
def edit(user_id: int, inertia: InertiaDepends, user: CurrentUser):
    target_user = USERS.get(user_id)
    if not target_user:
        return RedirectResponse(url="/users", status_code=303)

    user_safe = {k: v for k, v in target_user.items() if k != "password"}

    return inertia.render("Users/Edit", {"user": user_safe})


@router.put("/{user_id}")
def update(
    user_id: int,
    inertia: InertiaDepends,
    user: CurrentUser,
    data: UserUpdate,
):
    target_user = USERS.get(user_id)
    if target_user:
        target_user.update({
            "first_name": data.first_name,
            "last_name": data.last_name,
            "email": data.email,
            "owner": data.owner,
        })

        # Flash success message
        inertia.flash("success", f"User '{data.first_name} {data.last_name}' updated successfully.")

    return RedirectResponse(url=f"/users/{user_id}/edit", status_code=303)


@router.delete("/{user_id}")
def destroy(user_id: int, inertia: InertiaDepends, user: CurrentUser):
    target_user = USERS.get(user_id)
    if target_user:
        target_user["deleted_at"] = datetime.now().isoformat()

        # Flash warning message
        inertia.flash("warning", f"User '{target_user['first_name']} {target_user['last_name']}' has been deleted.")

    return RedirectResponse(url="/users", status_code=303)


@router.put("/{user_id}/restore")
def restore(user_id: int, inertia: InertiaDepends, user: CurrentUser):
    target_user = USERS.get(user_id)
    if target_user:
        target_user["deleted_at"] = None

        # Flash info message
        inertia.flash("info", f"User '{target_user['first_name']} {target_user['last_name']}' has been restored.")

    return RedirectResponse(url="/users", status_code=303)
