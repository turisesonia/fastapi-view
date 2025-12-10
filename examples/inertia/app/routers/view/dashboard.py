import time
from fastapi import APIRouter
from fastapi_view.inertia import InertiaDepends

from app.data import CONTACTS, ORGANIZATIONS, USERS
from app.security import CurrentUser

router = APIRouter(tags=["dashboard"])


def get_statistics():
    """Simulate expensive computation for statistics"""
    time.sleep(0.5)  # Simulate slow computation

    active_users = [u for u in USERS.values() if u["deleted_at"] is None]
    active_orgs = [o for o in ORGANIZATIONS.values() if o["deleted_at"] is None]
    active_contacts = [c for c in CONTACTS.values() if c["deleted_at"] is None]

    return {
        "total_users": len(active_users),
        "total_organizations": len(active_orgs),
        "total_contacts": len(active_contacts),
        "owner_users": len([u for u in active_users if u["owner"]]),
    }


def get_recent_activities():
    """Simulate expensive query for recent activities"""
    time.sleep(0.3)  # Simulate slow query

    return [
        {
            "id": 1,
            "type": "user_created",
            "description": "New user John Doe created",
            "timestamp": "2024-01-15T10:30:00Z",
        },
        {
            "id": 2,
            "type": "org_updated",
            "description": "Organization Acme Corporation updated",
            "timestamp": "2024-01-15T09:15:00Z",
        },
        {
            "id": 3,
            "type": "contact_created",
            "description": "New contact Alice Johnson created",
            "timestamp": "2024-01-14T16:45:00Z",
        },
    ]


def get_quick_stats():
    """Fast computation for immediate display"""
    return {
        "users": len(USERS),
        "organizations": len(ORGANIZATIONS),
        "contacts": len(CONTACTS),
    }


@router.get("/")
def dashboard(inertia: InertiaDepends, user: CurrentUser):
    return inertia.render(
        "Dashboard/Index",
        {
            # Fast data loaded immediately
            "quick_stats": get_quick_stats(),
            "user": {
                "name": f"{user['first_name']} {user['last_name']}",
                "email": user["email"],
            },
            # Slow data deferred - loads after initial page render
            "statistics": inertia.defer(get_statistics, group="analytics"),
            "recent_activities": inertia.defer(
                get_recent_activities, group="analytics"
            ),
            # Another deferred group for separate loading
            "chart_data": inertia.defer(
                lambda: {"labels": ["Jan", "Feb", "Mar"], "values": [10, 20, 15]},
                group="charts",
            ),
        },
    )
