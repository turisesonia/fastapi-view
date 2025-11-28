import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pyquery import PyQuery as pq

from fastapi_view import ViewDepends


@pytest.fixture
def app(monkeypatch) -> FastAPI:
    monkeypatch.setenv("FV_TEMPLATES_PATH", "tests/templates")

    app = FastAPI(title="Test app")

    @app.get("/")
    def index(view: ViewDepends, name: str = "World"):
        return view.render("index", {"name": name})

    @app.get("/about")
    def about(view: ViewDepends, message: str = "Hello World"):
        return view.render("about", {"message": message})

    return app


def test_view_response(app: FastAPI):
    with TestClient(app) as client:
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "index.html"


def test_access_about(app: FastAPI):
    with TestClient(app) as client:
        message = "This is about page"
        response = client.get("/about", params={"message": message})

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "about.html"

        d = pq(response.text)
        h = d("#title")

        assert h.text() == message
