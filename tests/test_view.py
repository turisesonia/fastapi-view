import os

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from fastapi_view import view, view_request

from fastapi_view.middleware import ViewRequestMiddleware

app_name = "Test fastapi app"
app = FastAPI(title=app_name)

view.views_directory = f"{os.path.abspath('tests')}/resources/views"

client = TestClient(app)
app.add_middleware(ViewRequestMiddleware)


@app.get("/")
def index(name: str = "World"):
    return view("index", {"name": name})


client = TestClient(app)


def test_view_response():
    response = client.get("/")

    assert response.ok
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.template.name == "index.html"


def test_view_get_templates():
    from fastapi.templating import Jinja2Templates

    assert isinstance(view.templates, Jinja2Templates)