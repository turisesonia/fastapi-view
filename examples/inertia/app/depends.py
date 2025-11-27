import typing as t
from fastapi import Depends, Request, HTTPException, status
from fastapi.templating import Jinja2Templates

from fastapi_view.inertia import (
    Inertia,
    InertiaSettings,
    ViteSettings,
    get_inertia_context,
)

from .config import (
    VIEWS_PATH,
    INERTIA_ROOT_TEMPLATE,
    INERTIA_ASSETS_VERSION,
    VITE_DEV_MODE,
    VITE_MANIFEST_PATH,
    VITE_DIST_PATH,
    VITE_DIST_URI_PREFIX,
)

# Inertia 設定
inertia_config = InertiaSettings(
    root_template=INERTIA_ROOT_TEMPLATE,
    assets_version=INERTIA_ASSETS_VERSION,
    vite_config=ViteSettings(
        dev_mode=VITE_DEV_MODE,
        manifest_path=VITE_MANIFEST_PATH,
        dist_path=VITE_DIST_PATH,
        dist_uri_prefix=VITE_DIST_URI_PREFIX,
    ),
)


def inertia_with_shared_props(templates: Jinja2Templates, config: InertiaSettings):
    """建立包含 shared props 的 Inertia 依賴"""

    def _dependency(request: Request):
        inertia_instance = get_inertia_context(templates, config)(request)

        # 設定 shared props - 將用戶資訊共享給所有頁面
        user = get_current_user(request)
        inertia_instance.share("auth", {"user": user})

        return inertia_instance

    return _dependency


# Inertia 依賴注入
InertiaDepend = t.Annotated[
    Inertia,
    Depends(
        inertia_with_shared_props(
            templates=Jinja2Templates(directory=VIEWS_PATH),
            config=inertia_config,
        )
    ),
]


# 認證相關依賴
def get_current_user(request: Request) -> dict | None:
    """取得當前登入用戶"""
    return request.session.get("user")


def require_login(request: Request) -> dict:
    """要求用戶登入的依賴"""
    user = get_current_user(request)
    if not user:
        # 使用 Inertia 重定向到登入頁面
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, headers={"Location": "/auth/login"}
        )
    return user


# 認證依賴的類型註解
CurrentUser = t.Annotated[dict | None, Depends(get_current_user)]
RequireLogin = t.Annotated[dict, Depends(require_login)]
