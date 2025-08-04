import os
import typing as t
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient
from jinja2 import Template
from pyquery import PyQuery as pq

from fastapi_view.view import View, view_factory

templates_path = Path(os.path.abspath("tests/templates"))


def test_initital_view():
    view = View(
        templates=Jinja2Templates(directory=templates_path),
        request=Request(scope={"type": "http", "path": "/"}),
    )

    assert isinstance(view._templates, Jinja2Templates)
    assert isinstance(view._templates.get_template("index.html"), Template)


app = FastAPI(title="Test app")

ViewDepends = t.Annotated[View, Depends(view_factory(templates_path))]


@app.get("/")
def index(view: ViewDepends, name: str = "World"):
    return view.render("index", {"name": name})


@app.get("/about")
def about(view: ViewDepends, message: str = "Hello World"):
    return view.render("about", {"message": message})


def test_view_response():
    with TestClient(app) as client:
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "index.html"


def test_access_about():
    with TestClient(app) as client:
        message = "This is about page"
        response = client.get("/about", params={"message": message})

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "about.html"

        d = pq(response.text)
        h = d("#title")

        assert h.text() == message
