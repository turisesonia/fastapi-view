from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers.view.auth import router as auth_router
from app.routers.view.dashboard import router as dashboard_router
from app.routers.view.organizations import router as organizations_router
from app.routers.view.contacts import router as contacts_router
from app.routers.view.users import router as users_router
from app.routers.view.merge_demo import router as merge_demo_router


app = FastAPI(title="FastAPI Inertia.js Demo", description="A demo app showcasing FastAPI-View Inertia.js integration", version="0.1.0")

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)

if settings.STATIC_PATH.exists():
    app.mount("/public", StaticFiles(directory=settings.STATIC_PATH), name="public")

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(organizations_router)
app.include_router(contacts_router)
app.include_router(users_router)
app.include_router(merge_demo_router)
