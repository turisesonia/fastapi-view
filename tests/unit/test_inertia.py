import json
from unittest.mock import Mock, patch

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse, Response

from fastapi_view.inertia import Inertia
from fastapi_view.inertia.enums import InertiaHeader
from fastapi_view.inertia.props import IgnoreFirstLoad, OptionalProp
from fastapi_view.view import ViewContext


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables"""
    monkeypatch.setenv("FV_INERTIA_ROOT_TEMPLATE", "app.html")
    monkeypatch.setenv("FV_INERTIA_ASSETS_VERSION", "1.0.0")


@pytest.fixture
def mock_request() -> Mock:
    """Create mock Request object"""
    request = Mock(spec=Request)
    request.headers = {}
    request.url = "http://test.com/"

    return request


@pytest.fixture
def mock_view_instance(mock_request: Mock) -> Mock:
    """Create mock ViewContext instance"""
    mock_view = Mock(spec=ViewContext)
    mock_view._request = mock_request

    return mock_view


@pytest.fixture
def inertia(mock_request: Mock, mock_view_instance: Mock) -> Inertia:
    """Create Inertia instance with mocked ViewContext"""
    with patch("fastapi_view.inertia.inertia.ViewContext") as mock_view_cls:
        mock_view_cls.return_value = mock_view_instance
        inertia_instance = Inertia(request=mock_request)

        return inertia_instance


def test_inertia_init(mock_request, mock_view_instance):
    """Test Inertia initialization"""
    with patch("fastapi_view.inertia.inertia.ViewContext") as mock_view_cls:
        mock_view_cls.return_value = mock_view_instance
        inertia = Inertia(request=mock_request)

        mock_view_cls.assert_called_once_with(mock_request)
        assert inertia._view == mock_view_instance
        assert inertia._root_template == "app.html"
        assert inertia._assets_version == "1.0.0"


@pytest.mark.parametrize(
    "partial_only,partial_component,component,expected",
    [
        (None, None, None, False),
        ("name,age", "TestComponent", None, False),
        ("name,age", "TestComponent", "DifferentComponent", False),
        ("name,age", "TestComponent", "TestComponent", True),
    ],
)
def test_is_partial_request(
    mock_request, inertia, partial_only, partial_component, component, expected
):
    """Test _is_partial_request property"""
    if partial_only:
        mock_request.headers[InertiaHeader.PARTIAL_ONLY] = partial_only
    if partial_component:
        mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = partial_component
    if component:
        inertia._component = component

    assert inertia._is_partial_request is expected


@pytest.mark.parametrize(
    "header_value,expected",
    [
        (None, [""]),
        ("name", ["name"]),
        ("name, age , email", ["name", "age", "email"]),
    ],
)
def test_partial_only_keys(mock_request, inertia, header_value, expected):
    """Test _partial_only_keys property"""
    if header_value:
        mock_request.headers[InertiaHeader.PARTIAL_ONLY] = header_value

    assert inertia._partial_only_keys == expected


@pytest.mark.parametrize(
    "header_value,expected",
    [
        (None, [""]),
        ("password", ["password"]),
        ("password, secret , token", ["password", "secret", "token"]),
    ],
)
def test_partial_except_keys(mock_request, inertia, header_value, expected):
    """Test _partial_except_keys property"""
    if header_value:
        mock_request.headers[InertiaHeader.PARTIAL_EXCEPT] = header_value

    assert inertia._partial_except_keys == expected


@pytest.mark.parametrize(
    "props,expected",
    [
        (
            {"name": "John", "age": 30, "email": "john@example.com"},
            {"name": "John", "age": 30, "email": "john@example.com"},
        ),
        (
            {"name": "John", "age": 30, "lazy_data": IgnoreFirstLoad()},
            {"name": "John", "age": 30},
        ),
        ({"lazy1": IgnoreFirstLoad(), "lazy2": OptionalProp("value")}, {}),
    ],
)
def test_resolve_partial_props_non_partial_request(inertia, props, expected):
    """Test _resolve_partial_props with non-partial request"""
    result = inertia._resolve_partial_props(props)

    assert result == expected


def test_resolve_partial_props_partial_request(mock_request, inertia):
    """Test _resolve_partial_props with partial request"""
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "name,age"
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    inertia._component = "TestComponent"

    props = {"name": "John", "age": 30, "email": "john@example.com"}
    result = inertia._resolve_partial_props(props)

    assert result == {"name": "John", "age": 30}


def test_resolve_partial_props_with_except_keys(mock_request, inertia):
    """Test _resolve_partial_props with except keys"""
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "name,age,password"
    mock_request.headers[InertiaHeader.PARTIAL_EXCEPT] = "password"
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    inertia._component = "TestComponent"

    props = {"name": "John", "age": 30, "password": "secret"}
    result = inertia._resolve_partial_props(props)

    assert result == {"name": "John", "age": 30}


def test_resolve_partial_props_no_matching_keys(mock_request, inertia):
    """Test _resolve_partial_props with no matching keys"""
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "nonexistent"
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    inertia._component = "TestComponent"

    props = {"name": "John", "age": 30}
    result = inertia._resolve_partial_props(props)

    assert result == {}


def test_resolve_partial_props_ignore_first_load_in_partial(mock_request, inertia):
    """Test _resolve_partial_props with IgnoreFirstLoad in partial request"""
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "name,lazy_data"
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    inertia._component = "TestComponent"

    lazy_prop = IgnoreFirstLoad()
    props = {"name": "John", "age": 30, "lazy_data": lazy_prop}
    result = inertia._resolve_partial_props(props)

    assert result == {"name": "John", "lazy_data": lazy_prop}


def test_resolve_callable_props_basic_functions(inertia):
    """Test _resolve_callable_props with basic functions"""
    props = {
        "name": "John",
        "message": lambda: "Hello World",
        "static": "unchanged",
    }
    result = inertia._resolve_callable_props(props)

    assert result == {"name": "John", "message": "Hello World", "static": "unchanged"}


def test_resolve_callable_props_nested_dicts(inertia):
    """Test _resolve_callable_props with nested dictionaries"""
    props = {
        "user": {
            "name": "Alice",
            "get_permissions": lambda: ["read", "write"],
            "age": 25,
        },
        "callback": lambda: "top_level",
    }
    result = inertia._resolve_callable_props(props)

    assert result == {
        "user": {"name": "Alice", "get_permissions": ["read", "write"], "age": 25},
        "callback": "top_level",
    }


def test_resolve_callable_props_no_recursive_on_returned_dicts(inertia):
    """Test _resolve_callable_props does not recursively process returned dictionaries"""

    def get_dict_with_callable():
        return {"nested_func": lambda: "not_called", "value": "static"}

    props = {"data": get_dict_with_callable}
    result = inertia._resolve_callable_props(props)

    assert callable(result["data"]["nested_func"])
    assert result["data"]["value"] == "static"


def test_share_method():
    """Test share class method"""
    Inertia._share = {}

    Inertia.share("user", {"name": "John", "email": "john@example.com"})
    Inertia.share("app_name", "My App")

    assert Inertia._share == {
        "user": {"name": "John", "email": "john@example.com"},
        "app_name": "My App",
    }

    Inertia._share = {}


@pytest.mark.parametrize(
    "value",
    [
        "test_value",
        lambda: "lazy_value",
    ],
)
def test_optional_static_method(value):
    """Test optional static method"""
    optional_value = Inertia.optional(value)

    assert isinstance(optional_value, OptionalProp)


def test_build_page_data_basic(mock_request, inertia):
    """Test _build_page_data basic functionality"""
    inertia._component = "TestComponent"
    props = {"name": "John", "age": 30}

    result = inertia._build_page_data(props)

    assert result["version"] == "1.0.0"
    assert result["component"] == "TestComponent"
    assert result["props"] == {"name": "John", "age": 30}
    assert result["url"] == "http://test.com/"


def test_build_page_data_with_shared_props(mock_request, inertia):
    """Test _build_page_data includes shared data"""
    Inertia._share = {"app_name": "Test App", "version": "1.0"}
    inertia._component = "TestComponent"
    props = {"name": "John"}

    result = inertia._build_page_data(props)

    assert result["props"] == {"app_name": "Test App", "version": "1.0", "name": "John"}

    Inertia._share = {}


def test_build_page_data_with_callable_props(mock_request, inertia):
    """Test _build_page_data handles callable props"""
    inertia._component = "TestComponent"
    props = {"name": "John", "timestamp": lambda: "2024-01-01"}

    result = inertia._build_page_data(props)

    assert result["props"] == {"name": "John", "timestamp": "2024-01-01"}


def test_build_page_data_with_ignore_first_load(mock_request, inertia):
    """Test _build_page_data handles IgnoreFirstLoad"""
    inertia._component = "TestComponent"
    props = {
        "name": "John",
        "lazy_data": IgnoreFirstLoad(),
        "optional": OptionalProp("value"),
    }

    result = inertia._build_page_data(props)

    assert result["props"] == {"name": "John"}


def test_render_json_response(mock_request, inertia):
    """Test render method returns JSON response"""
    mock_request.headers[InertiaHeader.INERTIA] = "true"

    props = {"name": "John", "age": 30}
    response = inertia.render("TestComponent", props)

    assert isinstance(response, JSONResponse)
    assert response.headers[InertiaHeader.INERTIA] == "True"
    assert response.headers["Vary"] == "Accept"

    content = json.loads(response.body.decode())
    assert content["component"] == "TestComponent"
    assert content["props"] == {"name": "John", "age": 30}
    assert content["version"] == "1.0.0"


def test_render_html_response(mock_request, mock_view_instance, inertia):
    """Test render method returns HTML response"""
    mock_view_instance.render.return_value = Response(content="<html></html>")

    props = {"name": "John", "age": 30}
    inertia.render("TestComponent", props)

    mock_view_instance.render.assert_called_once()
    call_args = mock_view_instance.render.call_args

    assert call_args[0][0] == "app.html"
    assert "page" in call_args[0][1]

    page_data = json.loads(call_args[0][1]["page"])
    assert page_data["component"] == "TestComponent"
    assert page_data["props"] == {"name": "John", "age": 30}


def test_render_without_props(mock_request, inertia):
    """Test render method without passing props"""
    mock_request.headers[InertiaHeader.INERTIA] = "true"

    response = inertia.render("TestComponent")

    content = json.loads(response.body.decode())
    assert content["component"] == "TestComponent"
    assert content["props"] == {}
