import json
import os
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient
from pydantic import BaseModel
from pyquery import PyQuery as pq

from fastapi_view import inertia, setup_inertia_app


class Item(BaseModel):
    name: str
    time: datetime = datetime.now()
    description: str = None


@pytest.fixture()
def app(faker) -> FastAPI:
    app = setup_inertia_app(
        FastAPI(title="Test app"),
        root_template="inertia.html",
        templates=Jinja2Templates(
            directory=f"{os.path.abspath('tests')}/resources/views"
        ),
    )

    inertia.share("app_name", "Test App")

    @app.get("/")
    def index(name: str = ""):
        return inertia.render("Index", {"name": name})

    @app.get("/partial")
    def partial_response(name: str = ""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return inertia.render("Partial", {"now": now, "name": name})

    @app.get("/items")
    def items():
        items = (Item(name=faker.name(), description=faker.text()) for _ in range(5))

        return inertia.render("Item", {"items": items})

    @app.get("/lazy")
    def lazy():
        return inertia.render(
            "Index",
            {
                "name": "name",
                "items": inertia.lazy(lambda: [1, 2, 3, 4, 5]),
                "title": lambda: "Title",
            },
        )

    return app


def test_inertia_page(faker, app):
    name = faker.name()

    with TestClient(app) as client:
        response = client.get("/", params={"name": name})

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "inertia.html"

        d = pq(response.text)
        h = d("#app")
        data_page = json.loads(h.attr("data-page"))

        assert "version" in data_page
        assert "url" in data_page
        assert data_page["component"] == "Index"
        assert data_page["props"]["name"] == name


def test_inertia_json(faker, app):
    name = faker.name()

    with TestClient(app) as client:
        response = client.get("/", headers={"X-Inertia": "true"}, params={"name": name})

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert response.headers["vary"] == "Accept"
        assert response.headers["x-inertia"] == "True"

        data = response.json()

        assert "version" in data
        assert "url" in data
        assert data["props"]["name"] == name
        assert data["component"] == "Index"


def test_inertia_partial_json(faker, app):
    name = faker.name()

    with TestClient(app) as client:
        response = client.get(
            "/partial",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "Partial",
                "X-Inertia-Partial-Data": "now",
            },
            params={"name": name},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert response.headers["vary"] == "Accept"
        assert response.headers["x-inertia"] == "True"

        data = response.json()

        assert "version" in data
        assert "url" in data
        assert "name" not in data["props"]
        assert "now" in data["props"]
        assert data["component"] == "Partial"


def test_inertia_share(faker, app):
    with TestClient(app) as client:
        name = faker.name()

        response = client.get("/", params={"name": name})

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "inertia.html"

        d = pq(response.text)
        h = d("#app")
        data_page = json.loads(h.attr("data-page"))

        assert "version" in data_page
        assert "url" in data_page
        assert data_page["component"] == "Index"
        assert data_page["props"]["name"] == name
        assert data_page["props"]["app_name"] == "Test App"


def test_inertia_version_outdated(app):
    os.environ["INERTIA_ASSETS_VERSION"] = "test.version"

    name = "testname"

    with TestClient(app) as client:
        response = client.get(
            "/", params={"name": name}, headers={"X-Inertia-Version": "2234"}
        )

        assert response.status_code == 409
        assert "x-inertia-location" in response.headers
        assert (
            response.headers["x-inertia-location"] == f"{client.base_url}/?name={name}"
        )


def test_inertia_response_with_pydantic(faker, app):
    with TestClient(app) as client:
        response = client.get("/items", headers={"X-Inertia": "true"})

        data = response.json()
        items = data["props"]["items"]

        assert isinstance(items, list)

        for item in items:
            assert isinstance(item, dict)


def test_inertia_lazy(faker, app):
    with TestClient(app) as client:
        response = client.get(
            "/lazy",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "Index",
                "X-Inertia-Partial-Data": "items",
            },
        )

        data = response.json()

        assert data["component"] == "Index"
        assert data["props"]["items"] == [1, 2, 3, 4, 5]
        assert "title" not in data["props"]

        response = client.get(
            "/lazy",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "Index",
                "X-Inertia-Partial-Data": "items,title",
            },
        )

        data = response.json()

        assert data["component"] == "Index"
        assert data["props"]["items"] == [1, 2, 3, 4, 5]
        assert data["props"]["title"] == "Title"
