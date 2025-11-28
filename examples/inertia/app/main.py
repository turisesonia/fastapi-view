from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers.view.home import router as home_router
from app.routers.view.auth import router as auth_router
from app.routers.view.product import router as product_router


app = FastAPI(title="FastAPI Inertia.js Example", description="", version="0.0.1")

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)

if settings.STATIC_PATH.exists():
    app.mount("/public", StaticFiles(directory=settings.STATIC_PATH), name="public")

app.include_router(auth_router)
app.include_router(home_router)
app.include_router(product_router)
