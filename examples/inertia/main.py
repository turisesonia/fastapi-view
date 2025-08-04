import os
import typing as t
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from fastapi_view.inertia import Inertia, InertiaConfig, ViteConfig, inertia_dependency

APP_PATH: Path = Path(os.path.abspath(""))
DIST_PATH: Path = APP_PATH / "dist"
RESOURCES_PATH: Path = APP_PATH / "resources"
VIEWS_PATH: Path = RESOURCES_PATH / "views"


inertia_config = InertiaConfig(
    root_template="app.html",
    assets_version="1.0.0",
    vite_config=ViteConfig(
        # dev_mode=True, # Uncomment this line to enable development mode
        manifest_path=Path(APP_PATH, "dist", ".vite", "manifest.json"),
        dist_path=Path(APP_PATH, "dist"),
        dist_uri_prefix="/public",
    ),
)


InertiaDepend = t.Annotated[
    Inertia,
    Depends(
        inertia_dependency(
            templates=Jinja2Templates(directory=VIEWS_PATH),
            config=inertia_config,
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
    return inertia.render("Index")


@app.get("/about")
def about(inertia: InertiaDepend):
    return inertia.render("About")


@app.get("/items")
def items(inertia: InertiaDepend):
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
