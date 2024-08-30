import os
from datetime import datetime

import pytest
from faker import Faker
from fastapi import FastAPI
from pytest_mock import MockerFixture

from fastapi_view import inertia, init_jinja2_templates, view
from fastapi_view.middleware import ViewRequestMiddleware


@pytest.fixture
def mocker(mocker: MockerFixture) -> MockerFixture:
    return mocker


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture()
def app() -> FastAPI:
    app = FastAPI(title="Test app")
    app.add_middleware(ViewRequestMiddleware)

    init_jinja2_templates(f"{os.path.abspath('tests')}/resources/views")

    inertia.share("app_name", "Test App")

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

        return inertia.render("Partial", {"now": now, "name": name})

    return app
