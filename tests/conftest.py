import os
import pytest

from datetime import datetime

from fastapi import FastAPI
from fastapi_view import view, inertia
from fastapi_view.middleware import ViewRequestMiddleware


@pytest.fixture()
def app():
    app = FastAPI(title="Test app")
    view.views_directory = f"{os.path.abspath('tests')}/resources/views"
    app.add_middleware(ViewRequestMiddleware)

    @app.get("/")
    def index(name: str = "World"):
        return view("index", {"name": name})

    @app.get("/about")
    def about(message: str = "Hello World"):
        return view("about", {"message": message})

    @app.get("/inertia")
    def inertia_index(name: str = ""):
        return inertia.render("Index", {"name": name})

    @app.get("/inertia/partial")
    def inertia_partial(name: str = ""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return inertia.render(
            "Partial",
            {"now": now, "name": name},
        )

    return app
