from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import DIST_PATH, SESSION_SECRET_KEY
from examples.inertia.app.product.view import router as product_router
from examples.inertia.app.home.view import router as home_router
from examples.inertia.app.auth.view import router as auth_router

app = FastAPI(
    title="FastAPI View - Feature Organized Example",
    description="按功能分組的 FastAPI + Inertia.js 範例應用",
    version="1.0.0",
)

# 配置 Session 中介軟體
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

app.mount("/public", StaticFiles(directory=DIST_PATH), name="public")

app.include_router(auth_router)
app.include_router(home_router)
app.include_router(product_router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "FastAPI View application is running"}
