from datetime import datetime
from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
from fastapi_view.inertia import InertiaDepends

from app.data import ORGANIZATIONS, CONTACTS, get_next_id
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.security import CurrentUser
from typing import Annotated

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("")
def index(
    inertia: InertiaDepends,
    user: CurrentUser,
    search: Annotated[str, Query()] = "",
    trashed: Annotated[str, Query()] = "",
):
    orgs = list(ORGANIZATIONS.values())

    if search:
        orgs = [o for o in orgs if search.lower() in o["name"].lower()]

    if trashed == "only":
        orgs = [o for o in orgs if o["deleted_at"] is not None]
    elif trashed != "with":
        orgs = [o for o in orgs if o["deleted_at"] is None]

    orgs_with_contacts = []
    for org in orgs:
        contact_count = sum(1 for c in CONTACTS.values() if c["organization_id"] == org["id"] and c["deleted_at"] is None)
        orgs_with_contacts.append({**org, "contacts_count": contact_count})

    return inertia.render(
        "Organizations/Index",
        {
            "organizations": orgs_with_contacts,
            "filters": {"search": search, "trashed": trashed},
        },
    )


@router.get("/create")
def create(inertia: InertiaDepends, user: CurrentUser):
    return inertia.render("Organizations/Create")


@router.post("")
def store(
    inertia: InertiaDepends,
    user: CurrentUser,
    data: OrganizationCreate,
):
    org_id = get_next_id("organization")
    ORGANIZATIONS[org_id] = {
        "id": org_id,
        "name": data.name,
        "email": data.email,
        "phone": data.phone,
        "address": data.address,
        "city": data.city,
        "region": data.region,
        "country": data.country,
        "postal_code": data.postal_code,
        "deleted_at": None,
    }

    return RedirectResponse(url="/organizations", status_code=303)


@router.get("/{org_id}/edit")
def edit(org_id: int, inertia: InertiaDepends, user: CurrentUser):
    org = ORGANIZATIONS.get(org_id)
    if not org:
        return RedirectResponse(url="/organizations", status_code=303)

    return inertia.render("Organizations/Edit", {"organization": org})


@router.put("/{org_id}")
def update(
    org_id: int,
    inertia: InertiaDepends,
    user: CurrentUser,
    data: OrganizationUpdate,
):
    org = ORGANIZATIONS.get(org_id)
    if org:
        org.update({
            "name": data.name,
            "email": data.email,
            "phone": data.phone,
            "address": data.address,
            "city": data.city,
            "region": data.region,
            "country": data.country,
            "postal_code": data.postal_code,
        })

    return RedirectResponse(url=f"/organizations/{org_id}/edit", status_code=303)


@router.delete("/{org_id}")
def destroy(org_id: int, user: CurrentUser):
    org = ORGANIZATIONS.get(org_id)
    if org:
        org["deleted_at"] = datetime.now().isoformat()

    return RedirectResponse(url="/organizations", status_code=303)


@router.put("/{org_id}/restore")
def restore(org_id: int, user: CurrentUser):
    org = ORGANIZATIONS.get(org_id)
    if org:
        org["deleted_at"] = None

    return RedirectResponse(url="/organizations", status_code=303)
