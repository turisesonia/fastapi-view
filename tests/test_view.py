from fastapi.testclient import TestClient
from pyquery import PyQuery as pq


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
