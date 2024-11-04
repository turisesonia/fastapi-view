import os
from pathlib import Path

from fastapi import FastAPI

from fastapi_view import inertia

from .schemas import Item

ABS_PATH = Path(os.path.abspath("examples/inertia"))
RESOURCES_PATH = ABS_PATH / "resources"
VIEWS_PATH = RESOURCES_PATH / "views"


os.environ["VITE_DEV_MODE"] = "True"
os.environ["VITE_MANIFEST_PATH"] = Path(ABS_PATH, "dist", "manifest.json").as_posix()
os.environ["VITE_DIST_PATH"] = (ABS_PATH / "dist").as_posix()
os.environ["VITE_DIST_URI_PREFIX"] = "static"


app = FastAPI(title="Test app")
inertia.setup(app, directory=VIEWS_PATH, use_vite=True)


@app.get("/")
def index():
    return inertia("Index")


@app.get("/about")
def about():
    return inertia("About")


@app.get("/items")
def items():
    items = (
        Item(
            id=n,
            name=f"item-{n}",
            price=n * 10,
            description=f"description-{n}",
        )
        for n in range(1, 6)
    )

    return inertia("Item", props={"items": items})
