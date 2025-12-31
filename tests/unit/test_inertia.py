import json
from unittest.mock import Mock, patch

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse, Response

from fastapi_view.inertia import Inertia
from fastapi_view.inertia.enums import InertiaHeader
from fastapi_view.inertia.inertia import FLASH_PROPS_KEY, REQUEST_SESSION_KEY
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
    request.session = None
    request.scope = {}

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


def test_resolve_property_instances_basic_functions(inertia):
    """Test _resolve_property_instances with basic functions"""
    props = {
        "name": "John",
        "message": lambda: "Hello World",
        "static": "unchanged",
    }
    result = inertia._resolve_property_instances(props)

    assert result == {"name": "John", "message": "Hello World", "static": "unchanged"}


def test_resolve_property_instances_nested_dicts(inertia):
    """Test _resolve_property_instances with nested dictionaries"""
    props = {
        "user": {
            "name": "Alice",
            "get_permissions": lambda: ["read", "write"],
            "age": 25,
        },
        "callback": lambda: "top_level",
    }
    result = inertia._resolve_property_instances(props)

    assert result == {
        "user": {"name": "Alice", "get_permissions": ["read", "write"], "age": 25},
        "callback": "top_level",
    }


def test_resolve_property_instances_no_recursive_on_returned_dicts(inertia):
    """Test _resolve_property_instances does not recursively process returned dictionaries"""

    def get_dict_with_callable():
        return {"nested_func": lambda: "not_called", "value": "static"}

    props = {"data": get_dict_with_callable}
    result = inertia._resolve_property_instances(props)

    assert callable(result["data"]["nested_func"])
    assert result["data"]["value"] == "static"


def test_share_method(inertia):
    """Test share instance method"""
    inertia.share("user", {"name": "John", "email": "john@example.com"})
    inertia.share("app_name", "My App")

    assert inertia._share == {
        "user": {"name": "John", "email": "john@example.com"},
        "app_name": "My App",
    }


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


def test_build_page_object_basic(mock_request, inertia):
    """Test _build_page_object basic functionality"""
    inertia._component = "TestComponent"
    props = {"name": "John", "age": 30}

    result = inertia._build_page_object(props)

    assert result["version"] == "1.0.0"
    assert result["component"] == "TestComponent"
    assert result["props"] == {"flash": {}, "name": "John", "age": 30}
    assert result["url"] == "http://test.com/"


def test_build_page_object_with_shared_props(mock_request, inertia):
    """Test _build_page_object includes shared data"""
    inertia.share("app_name", "Test App")
    inertia.share("version", "1.0")
    inertia._component = "TestComponent"
    props = {"name": "John"}

    result = inertia._build_page_object(props)

    assert result["props"] == {
        "app_name": "Test App",
        "version": "1.0",
        "flash": {},
        "name": "John",
    }


def test_build_page_object_with_callable_props(mock_request, inertia):
    """Test _build_page_object handles callable props"""
    inertia._component = "TestComponent"
    props = {"name": "John", "timestamp": lambda: "2024-01-01"}

    result = inertia._build_page_object(props)

    assert result["props"] == {"flash": {}, "name": "John", "timestamp": "2024-01-01"}


def test_build_page_object_with_ignore_first_load(mock_request, inertia):
    """Test _build_page_object handles IgnoreFirstLoad"""
    inertia._component = "TestComponent"
    props = {
        "name": "John",
        "lazy_data": IgnoreFirstLoad(),
        "optional": OptionalProp("value"),
    }

    result = inertia._build_page_object(props)

    assert result["props"] == {"flash": {}, "name": "John"}


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
    assert content["props"] == {"flash": {}, "name": "John", "age": 30}
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
    assert page_data["props"] == {"flash": {}, "name": "John", "age": 30}


def test_render_without_props(mock_request, inertia):
    """Test render method without passing props"""
    mock_request.headers[InertiaHeader.INERTIA] = "true"

    response = inertia.render("TestComponent")

    content = json.loads(response.body.decode())
    assert content["component"] == "TestComponent"
    assert content["props"] == {"flash": {}}


@pytest.mark.parametrize(
    "scope,session,expected",
    [
        ({REQUEST_SESSION_KEY: True}, {"user": "John"}, {"user": "John"}),
        ({}, None, None),
    ],
)
def test_get_request_session(inertia, scope, session, expected):
    """Test _get_request_session returns session or None based on middleware availability"""
    inertia._request.scope = scope
    inertia._request.session = session

    result = inertia._get_request_session()

    assert result == expected


@pytest.mark.parametrize(
    "scope,session,expected",
    [
        ({}, None, {FLASH_PROPS_KEY: {}}),
        ({REQUEST_SESSION_KEY: True}, {"user": "John"}, {FLASH_PROPS_KEY: {}}),
        (
            {REQUEST_SESSION_KEY: True},
            {FLASH_PROPS_KEY: {"success": "Done"}},
            {FLASH_PROPS_KEY: {"success": "Done"}},
        ),
    ],
)
def test_get_flash_props(inertia, scope, session, expected):
    """Test _get_flash_props returns flash messages in proper format"""
    inertia._request.scope = scope
    inertia._request.session = session

    result = inertia._get_flash_props()

    assert result == expected


def test_flash_raises_error_without_session_middleware(inertia):
    """Test flash raises RuntimeError when SessionMiddleware is not installed"""
    inertia._request.scope = {}

    with pytest.raises(RuntimeError, match="SessionMiddleware must be installed"):
        inertia.flash("error", "This should fail")


def test_flash_adds_and_overwrites_messages(inertia):
    """Test flash adds new messages and overwrites existing ones"""
    mock_session = {}
    inertia._request.scope = {REQUEST_SESSION_KEY: True}
    inertia._request.session = mock_session

    inertia.flash("success", "First message")
    inertia.flash("error", "Error message")
    inertia.flash("success", "Overwritten message")

    assert mock_session[FLASH_PROPS_KEY] == {
        "success": "Overwritten message",
        "error": "Error message",
    }


def test_flash_messages_are_removed_after_reading(inertia):
    """Test flash messages are removed from session after being read"""
    mock_session = {
        FLASH_PROPS_KEY: {"success": "Test message", "info": "Another message"}
    }

    inertia._request.scope = {REQUEST_SESSION_KEY: True}
    inertia._request.session = mock_session

    # First read should return the flash messages in proper format
    result = inertia._get_flash_props()

    assert result == {
        FLASH_PROPS_KEY: {"success": "Test message", "info": "Another message"}
    }
    assert FLASH_PROPS_KEY not in mock_session

    # Second read should return empty flash dict (session is still available)
    result_second = inertia._get_flash_props()

    assert result_second == {FLASH_PROPS_KEY: {}}


@pytest.mark.parametrize(
    "value",
    ["string", 123, {"key": "val"}, ["list"]],
)
def test_flash_supports_various_value_types(inertia, value):
    """Test flash supports various data types"""
    mock_session = {}
    inertia._request.scope = {REQUEST_SESSION_KEY: True}
    inertia._request.session = mock_session

    inertia.flash("data", value)

    assert mock_session[FLASH_PROPS_KEY]["data"] == value


@pytest.mark.parametrize(
    "scope,session,shared_data,expected_props",
    [
        ({}, None, {}, {"flash": {}, "user": "John"}),
        (
            {REQUEST_SESSION_KEY: True},
            {FLASH_PROPS_KEY: {"success": "Done"}},
            {},
            {"flash": {"success": "Done"}, "user": "John"},
        ),
        (
            {REQUEST_SESSION_KEY: True},
            {FLASH_PROPS_KEY: {"error": "Failed"}},
            {"app": "Test"},
            {"app": "Test", "flash": {"error": "Failed"}, "user": "John"},
        ),
    ],
)
def test_build_page_object_with_flash_integration(
    inertia, scope, session, shared_data, expected_props
):
    """Test _build_page_object correctly merges flash, shared, and regular props"""
    for key, value in shared_data.items():
        inertia.share(key, value)
    inertia._request.scope = scope
    inertia._request.session = session
    inertia._component = "TestComponent"

    result = inertia._build_page_object({"user": "John"})

    assert result["props"] == expected_props


def test_deferred_props_excluded_on_initial_load(inertia):
    """Test deferred props are excluded from initial load"""
    from fastapi_view.inertia.props import DeferredProp

    inertia._component = "TestComponent"
    props = {
        "user": {"name": "John"},
        "posts": DeferredProp(lambda: ["post1", "post2"], group="content"),
        "stats": DeferredProp(lambda: {"views": 100}, group="analytics"),
    }

    result = inertia._build_page_object(props)

    # Deferred props should NOT be in resolved props
    assert "posts" not in result["props"]
    assert "stats" not in result["props"]
    assert "user" in result["props"]

    # deferredProps config should be present
    assert "deferredProps" in result
    assert result["deferredProps"] == {
        "content": ["posts"],
        "analytics": ["stats"],
    }


def test_deferred_props_resolved_on_partial_request(mock_request, inertia):
    """Test deferred props are resolved during partial request"""
    from fastapi_view.inertia.props import DeferredProp

    # Setup partial request
    mock_request.headers[InertiaHeader.INERTIA] = "true"
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "posts"
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    inertia._component = "TestComponent"

    # Create props with deferred prop
    props = {
        "user": {"name": "John"},
        "posts": DeferredProp(lambda: ["post1", "post2"], group="content"),
    }

    result = inertia._build_page_object(props)

    # Only requested deferred prop should be resolved
    assert "posts" in result["props"]
    assert result["props"]["posts"] == ["post1", "post2"]
    assert "user" not in result["props"]  # Not requested

    # deferredProps config should NOT be present for partial requests
    assert "deferredProps" not in result


def test_deferred_props_with_multiple_groups(inertia):
    """Test multiple deferred props can be grouped"""
    from fastapi_view.inertia.props import DeferredProp

    inertia._component = "TestComponent"
    props = {
        "posts": DeferredProp(lambda: [], group="content"),
        "comments": DeferredProp(lambda: [], group="content"),
        "analytics": DeferredProp(lambda: {}, group="metrics"),
        "stats": DeferredProp(lambda: {}, group="metrics"),
    }

    result = inertia._build_page_object(props)

    assert result["deferredProps"] == {
        "content": ["posts", "comments"],
        "metrics": ["analytics", "stats"],
    }


def test_inertia_defer_helper_method():
    """Test Inertia.defer() static method"""
    from fastapi_view.inertia.props import DeferredProp

    deferred = Inertia.defer(lambda: "data", group="test")

    assert isinstance(deferred, DeferredProp)
    assert deferred.group == "test"
    assert deferred() == "data"


def test_deferred_props_default_group(inertia):
    """Test deferred props use default group when not specified"""
    from fastapi_view.inertia.props import DeferredProp

    inertia._component = "TestComponent"
    props = {
        "data1": DeferredProp(lambda: "value1"),  # No group specified
        "data2": DeferredProp(lambda: "value2"),  # No group specified
    }

    result = inertia._build_page_object(props)

    assert result["deferredProps"] == {
        "default": ["data1", "data2"],
    }


def test_deferred_props_mixed_with_regular_props(inertia):
    """Test deferred props work alongside regular props"""
    from fastapi_view.inertia.props import DeferredProp

    inertia._component = "TestComponent"
    props = {
        "user": {"name": "John"},
        "count": 42,
        "posts": DeferredProp(lambda: ["post1"], group="content"),
        "active": True,
    }

    result = inertia._build_page_object(props)

    # Regular props should be present
    assert result["props"]["user"] == {"name": "John"}
    assert result["props"]["count"] == 42
    assert result["props"]["active"] is True

    # Deferred prop should NOT be in props
    assert "posts" not in result["props"]

    # Deferred config should be present
    assert result["deferredProps"] == {"content": ["posts"]}
