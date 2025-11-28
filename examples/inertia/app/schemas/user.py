from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    owner: bool = False


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    owner: bool = False
