import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi_view import inertia, view
from fastapi_view.middleware import ViewRequestMiddleware

from .schemas import Item

EXAMPLE_APP_PATH = os.path.abspath("example")

os.environ["VITE_MANIFEST_PATH"] = Path(
    EXAMPLE_APP_PATH, "dist", "manifest.json"
).as_posix()


@asynccontextmanager
async def lifespan(app: FastAPI):
    view.initialize(Jinja2Templates(directory="./example/views"), use_vite=True)
    yield


app = FastAPI(title="Test app", lifespan=lifespan)

app.add_middleware(ViewRequestMiddleware, use_inertia=True)
app.mount(
    "/assets",
    StaticFiles(directory=Path(EXAMPLE_APP_PATH, "dist", "assets")),
    name="assets",
)


@app.get("/")
def index():
    return inertia.render("Index")


@app.get("/about")
def about():
    return inertia.render("About")


@app.get("/items")
def items():
    items = (
        Item(
            name=f"item-{n}",
            description=f"description-{n}",
        )
        for n in range(5)
    )

    return inertia.render("Item", props={"items": items})
