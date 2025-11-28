from pydantic import BaseModel, EmailStr


class ContactCreate(BaseModel):
    organization_id: int | None = None
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    postal_code: str | None = None


class ContactUpdate(BaseModel):
    organization_id: int | None = None
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    postal_code: str | None = None
