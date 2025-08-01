import os
import typing as t
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from fastapi_view import Inertia, inertia_factory
from fastapi_view.config import ViteConfig

APP_PATH: Path = Path(os.path.abspath(""))
DIST_PATH: Path = APP_PATH / "dist"
RESOURCES_PATH: Path = APP_PATH / "resources"
VIEWS_PATH: Path = RESOURCES_PATH / "views"


templates = Jinja2Templates(directory=VIEWS_PATH)

vite_config = ViteConfig(
    # dev_mode=True, # Uncomment this line to enable development mode
    manifest_path=Path(APP_PATH, "dist", ".vite", "manifest.json"),
    dist_path=Path(APP_PATH, "dist"),
    dist_uri_prefix="public",
)


InertiaDepend = t.Annotated[
    Inertia,
    Depends(
        inertia_factory(
            templates=templates,
            root_template="app.html",
            vite_config=vite_config,
        )
    ),
]

app = FastAPI(title="Test app")
app.mount("/public", StaticFiles(directory=DIST_PATH), name="public")


class Item(BaseModel):
    id: int
    name: str
    description: str = None
    price: int
    image: str = "https://api.lorem.space/image/game?w=150&h=220"


@app.get("/")
def index(inertia: InertiaDepend):
    print(id(inertia))
    return inertia.render("Index")


@app.get("/about")
def about(inertia: InertiaDepend):
    print(id(inertia))
    return inertia.render("About")


@app.get("/items")
def items(inertia: InertiaDepend):
    print(id(inertia))
    items = (
        Item(
            id=n,
            name=f"item-{n}",
            price=n * 10,
            description=f"description-{n}",
        )
        for n in range(1, 6)
    )

    return inertia.render("Item", props={"items": items})
