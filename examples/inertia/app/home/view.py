from fastapi import APIRouter, Depends

from ..depends import InertiaDepend, RequireLogin
from ..product.services import ProductService
from typing import Annotated

router = APIRouter(tags=["pages"])


@router.get("/")
def home(
    inertia: InertiaDepend,
    user: RequireLogin,
    product_service: Annotated[ProductService, Depends()],
):
    """首頁"""
    featured_products = product_service.get_featured_products()

    return inertia.render(
        "Home",
        {
            "title": f"歡迎 {user['display_name']} 使用 FastAPI View",
            "description": "這是一個使用 FastAPI 和 Vue.js 建立的專案",
            "technologies": ["FastAPI", "Vue 3", "Vite", "Tailwind CSS", "Inertia.js"],
            "features": [
                {"title": "按功能分組", "description": "清晰的程式碼組織結構"},
                {"title": "模組化設計", "description": "每個功能獨立開發和維護"},
                {"title": "類型安全", "description": "使用 Pydantic 進行資料驗證"},
            ],
            "featured_products": [
                product.model_dump() for product in featured_products
            ],
            "user": user,  # 傳遞用戶資訊到前端
        },
    )


@router.get("/about")
def about(inertia: InertiaDepend, user: RequireLogin):
    """關於頁面"""
    return inertia.render(
        "About",
        {
            "title": "FastAPI View 函式庫",
            "subtitle": "強大且易用的 FastAPI 前端整合方案",
            "features": [
                {"title": "快速整合", "description": "輕鬆整合 FastAPI 後端服務"},
                {
                    "title": "Inertia.js 支援",
                    "description": "支援 Inertia.js 以及 Vite",
                },
                {"title": "模組化架構", "description": "按功能分組的清晰架構"},
            ],
            "code_example": """
from fastapi import FastAPI, Depends
from fastapi_view.inertia import Inertia, get_inertia_context

app = FastAPI()

@app.get("/")
def index(inertia: Inertia = Depends(get_inertia_context)):
    return inertia.render("Index", {"message": "Hello World"})
""".strip(),
        },
    )
