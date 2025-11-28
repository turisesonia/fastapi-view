from typing import Annotated
from fastapi import APIRouter, Depends

from fastapi_view.inertia import InertiaDepends
from app.security import CurrentUser
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
def list_products(
    inertia: InertiaDepends,
    user: CurrentUser,
    service: Annotated[ProductService, Depends()],
):
    """商品列表頁面"""
    products = service.get_all_products()
    return inertia.render(
        "Products/Index", {"items": [product.model_dump() for product in products]}
    )


@router.get("/{product_id}")
def product_detail(
    product_id: int,
    inertia: InertiaDepends,
    user: CurrentUser,
    service: Annotated[ProductService, Depends()],
):
    """商品詳情頁面"""
    product = service.get_product_by_id(product_id)
    return inertia.render("Products/Detail", {"item": product.model_dump()})
