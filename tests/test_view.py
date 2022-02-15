import os

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient


from fastapi_view import view, inertia

app_name = "Test fastapi app"
app = FastAPI(title=app_name)


@app.get("/")
def index(request: Request, name: str = "World"):
    return view("index", {"request": request, "name": name})


@app.get("/inertia/component")
def inertia_index(request: Request):
    return inertia.render("Index", request=request, props={"name": "Index"})


view.views_directory = f"{os.path.abspath('tests')}/resources/views"

client = TestClient(app)


def test_view_response():
    response = client.get("/")

    assert response.ok
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.template.name == "index.html"
