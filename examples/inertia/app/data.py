from typing import TypedDict


class User(TypedDict):
    id: int
    first_name: str
    last_name: str
    email: str
    password: str
    owner: bool
    deleted_at: str | None


class Organization(TypedDict):
    id: int
    name: str
    email: str | None
    phone: str | None
    address: str | None
    city: str | None
    region: str | None
    country: str | None
    postal_code: str | None
    deleted_at: str | None


class Contact(TypedDict):
    id: int
    organization_id: int | None
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    address: str | None
    city: str | None
    region: str | None
    country: str | None
    postal_code: str | None
    deleted_at: str | None


USERS: dict[int, User] = {
    1: {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "secret",
        "owner": True,
        "deleted_at": None,
    },
    2: {
        "id": 2,
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "password": "secret",
        "owner": False,
        "deleted_at": None,
    },
}

ORGANIZATIONS: dict[int, Organization] = {
    1: {
        "id": 1,
        "name": "Acme Corporation",
        "email": "info@acme.com",
        "phone": "555-1234",
        "address": "123 Main St",
        "city": "New York",
        "region": "NY",
        "country": "US",
        "postal_code": "10001",
        "deleted_at": None,
    },
    2: {
        "id": 2,
        "name": "Tech Innovations Inc",
        "email": "contact@techinnovations.com",
        "phone": "555-5678",
        "address": "456 Tech Blvd",
        "city": "San Francisco",
        "region": "CA",
        "country": "US",
        "postal_code": "94105",
        "deleted_at": None,
    },
    3: {
        "id": 3,
        "name": "Global Solutions Ltd",
        "email": "hello@globalsolutions.com",
        "phone": "555-9012",
        "address": "789 Business Ave",
        "city": "London",
        "region": "England",
        "country": "GB",
        "postal_code": "SW1A 1AA",
        "deleted_at": None,
    },
}

CONTACTS: dict[int, Contact] = {
    1: {
        "id": 1,
        "organization_id": 1,
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice@acme.com",
        "phone": "555-1111",
        "address": "123 Main St",
        "city": "New York",
        "region": "NY",
        "country": "US",
        "postal_code": "10001",
        "deleted_at": None,
    },
    2: {
        "id": 2,
        "organization_id": 1,
        "first_name": "Bob",
        "last_name": "Williams",
        "email": "bob@acme.com",
        "phone": "555-2222",
        "address": "123 Main St",
        "city": "New York",
        "region": "NY",
        "country": "US",
        "postal_code": "10001",
        "deleted_at": None,
    },
    3: {
        "id": 3,
        "organization_id": 2,
        "first_name": "Charlie",
        "last_name": "Brown",
        "email": "charlie@techinnovations.com",
        "phone": "555-3333",
        "address": "456 Tech Blvd",
        "city": "San Francisco",
        "region": "CA",
        "country": "US",
        "postal_code": "94105",
        "deleted_at": None,
    },
    4: {
        "id": 4,
        "organization_id": None,
        "first_name": "Diana",
        "last_name": "Garcia",
        "email": "diana@email.com",
        "phone": "555-4444",
        "address": "321 Home St",
        "city": "Austin",
        "region": "TX",
        "country": "US",
        "postal_code": "73301",
        "deleted_at": None,
    },
}

next_user_id = 3
next_org_id = 4
next_contact_id = 5


def get_next_id(entity_type: str) -> int:
    global next_user_id, next_org_id, next_contact_id

    if entity_type == "user":
        current_id = next_user_id
        next_user_id += 1

        return current_id
    elif entity_type == "organization":
        current_id = next_org_id
        next_org_id += 1

        return current_id
    elif entity_type == "contact":
        current_id = next_contact_id
        next_contact_id += 1

        return current_id

    raise ValueError(f"Unknown entity type: {entity_type}")
