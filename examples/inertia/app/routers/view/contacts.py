from datetime import datetime
from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
from fastapi_view.inertia import InertiaDepends

from app.data import CONTACTS, ORGANIZATIONS, get_next_id
from app.schemas.contact import ContactCreate, ContactUpdate
from app.security import CurrentUser
from typing import Annotated

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("")
def index(
    inertia: InertiaDepends,
    user: CurrentUser,
    search: Annotated[str, Query()] = "",
    trashed: Annotated[str, Query()] = "",
):
    contacts = list(CONTACTS.values())

    if search:
        contacts = [
            c
            for c in contacts
            if search.lower() in c["first_name"].lower()
            or search.lower() in c["last_name"].lower()
        ]

    if trashed == "only":
        contacts = [c for c in contacts if c["deleted_at"] is not None]
    elif trashed != "with":
        contacts = [c for c in contacts if c["deleted_at"] is None]

    contacts_with_org = []
    for contact in contacts:
        org_name = None
        if contact["organization_id"]:
            org = ORGANIZATIONS.get(contact["organization_id"])
            org_name = org["name"] if org else None

        contacts_with_org.append(
            {**contact, "organization": {"name": org_name} if org_name else None}
        )

    return inertia.render(
        "Contacts/Index",
        {
            "contacts": contacts_with_org,
            "filters": {"search": search, "trashed": trashed},
        },
    )


@router.get("/create")
def create(inertia: InertiaDepends, user: CurrentUser):
    orgs = [
        {"id": o["id"], "name": o["name"]}
        for o in ORGANIZATIONS.values()
        if o["deleted_at"] is None
    ]

    return inertia.render("Contacts/Create", {"organizations": orgs})


@router.post("")
def store(
    inertia: InertiaDepends,
    user: CurrentUser,
    data: ContactCreate,
):
    contact_id = get_next_id("contact")

    CONTACTS[contact_id] = {
        "id": contact_id,
        "organization_id": data.organization_id,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "phone": data.phone,
        "address": data.address,
        "city": data.city,
        "region": data.region,
        "country": data.country,
        "postal_code": data.postal_code,
        "deleted_at": None,
    }

    return RedirectResponse(url="/contacts", status_code=303)


@router.get("/{contact_id}/edit")
def edit(contact_id: int, inertia: InertiaDepends, user: CurrentUser):
    contact = CONTACTS.get(contact_id)

    if not contact:
        return RedirectResponse(url="/contacts", status_code=303)

    orgs = [
        {"id": o["id"], "name": o["name"]}
        for o in ORGANIZATIONS.values()
        if o["deleted_at"] is None
    ]
    contact_with_org = dict(contact)
    if contact["organization_id"]:
        org = ORGANIZATIONS.get(contact["organization_id"])
        contact_with_org["organization"] = (
            {"id": org["id"], "name": org["name"]} if org else None
        )

    return inertia.render(
        "Contacts/Edit", {"contact": contact_with_org, "organizations": orgs}
    )


@router.put("/{contact_id}")
def update(
    contact_id: int,
    inertia: InertiaDepends,
    user: CurrentUser,
    data: ContactUpdate,
):
    contact = CONTACTS.get(contact_id)
    if contact:
        contact.update(
            {
                "organization_id": data.organization_id,
                "first_name": data.first_name,
                "last_name": data.last_name,
                "email": data.email,
                "phone": data.phone,
                "address": data.address,
                "city": data.city,
                "region": data.region,
                "country": data.country,
                "postal_code": data.postal_code,
            }
        )

    return RedirectResponse(url=f"/contacts/{contact_id}/edit", status_code=303)


@router.delete("/{contact_id}")
def destroy(contact_id: int, user: CurrentUser):
    contact = CONTACTS.get(contact_id)
    if contact:
        contact["deleted_at"] = datetime.now().isoformat()

    return RedirectResponse(url="/contacts", status_code=303)


@router.put("/{contact_id}/restore")
def restore(contact_id: int, user: CurrentUser):
    contact = CONTACTS.get(contact_id)
    if contact:
        contact["deleted_at"] = None

    return RedirectResponse(url="/contacts", status_code=303)
