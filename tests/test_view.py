import os

import pytest
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient
from pyquery import PyQuery as pq

from fastapi_view import inertia, view
from fastapi_view.middleware import ViewRequestMiddleware


@pytest.fixture()
def app() -> FastAPI:
    app = FastAPI(title="Test app")
    app.add_middleware(ViewRequestMiddleware)

    view.initialize(
        Jinja2Templates(directory=f"{os.path.abspath('tests')}/resources/views")
    )

    inertia.share("app_name", "Test App")

    @app.get("/")
    def index(name: str = "World"):
        return view("index", {"name": name})

    @app.get("/about")
    def about(message: str = "Hello World"):
        return view("about", {"message": message})

    return app


def test_view_response(app):
    with TestClient(app) as client:
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "index.html"


def test_access_about(app):
    with TestClient(app) as client:
        message = "This is about page"
        response = client.get("/about", params={"message": message})

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "about.html"

        d = pq(response.text)
        h = d("#title")

        assert h.text() == message
