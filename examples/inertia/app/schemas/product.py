from pydantic import BaseModel


class ProductSchema(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: int
    image: str = "https://api.lorem.space/image/game?w=150&h=220"