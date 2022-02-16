import os

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient


from fastapi_view import view

app_name = "Test fastapi app"
app = FastAPI(title=app_name)

view.views_directory = f"{os.path.abspath('tests')}/resources/views"


@app.get("/")
def index(request: Request, name: str = "World"):
    return view("index", {"request": request, "name": name})


client = TestClient(app)


def test_view_response():
    response = client.get("/")

    assert response.ok
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.template.name == "index.html"


def test_view_get_templates():
    from fastapi.templating import Jinja2Templates

    assert isinstance(view.templates, Jinja2Templates)