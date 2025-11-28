from jinja2.environment import Template
import pytest

from fastapi import Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from fastapi_view.view import ViewContext, get_view_context


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables"""
    monkeypatch.setenv("FV_TEMPLATES_PATH", "tests/templates")


@pytest.fixture
def test_request():
    return Request(scope={"type": "http", "path": "/"})


def test_view_context_init(test_request: Request):
    view = ViewContext(request=test_request)

    assert isinstance(view._templates, Jinja2Templates)
    assert isinstance(view._templates.get_template("index.html"), Template)


def test_view_context_init_raises_error_with_invalid_request():
    """Test ViewContext raises ValueError when request is not a Request instance"""

    with pytest.raises(
        ValueError, match="request instance type must be fastapi.Request"
    ):
        ViewContext(request="not a request")


def test_view_context_render(test_request: Request):
    """Test ViewContext.render returns Response with correct template"""

    view = ViewContext(request=test_request)
    response = view.render("index", {"name": "Test"})

    assert isinstance(response, Response)
    assert response.status_code == 200


def test_view_context_render_adds_html_extension(test_request: Request):
    """Test ViewContext.render automatically adds .html extension"""

    view = ViewContext(request=test_request)

    response_with_ext = view.render("index.html", {})
    response_without_ext = view.render("index", {})

    assert response_with_ext.status_code == 200
    assert response_without_ext.status_code == 200


def test_get_view_context(test_request: Request):
    """Test get_view_context returns ViewContext instance"""

    view = get_view_context(test_request)

    assert isinstance(view, ViewContext)
    assert isinstance(view._templates, Jinja2Templates)
