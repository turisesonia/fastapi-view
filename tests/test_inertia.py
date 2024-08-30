import json

from fastapi.testclient import TestClient
from pyquery import PyQuery as pq


def test_inertia_page(faker, app):
    name = faker.name()

    with TestClient(app) as client:
        response = client.get("/inertia", params={"name": name})

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "app.html"

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
        response = client.get(
            "/inertia", headers={"X-Inertia": "true"}, params={"name": name}
        )

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
            "/inertia/partial",
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

        response = client.get("/inertia", params={"name": name})

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "app.html"

        d = pq(response.text)
        h = d("#app")
        data_page = json.loads(h.attr("data-page"))

        assert "version" in data_page
        assert "url" in data_page
        assert data_page["component"] == "Index"
        assert data_page["props"]["name"] == name
        assert data_page["props"]["app_name"] == "Test App"
