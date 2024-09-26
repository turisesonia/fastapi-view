import json
import os
from datetime import datetime

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
    app.add_middleware(ViewRequestMiddleware, use_inertia=True)

    view.initialize(
        Jinja2Templates(directory=f"{os.path.abspath('tests')}/resources/views")
    )

    inertia.set_root_template("inertia.html")
    inertia.share("app_name", "Test App")

    @app.get("/")
    def index(name: str = ""):
        return inertia.render("Index", {"name": name})

    @app.get("/partial")
    def partial_response(name: str = ""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return inertia.render("Partial", {"now": now, "name": name})

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


def test_inertia_version_outdated(faker, app):
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
