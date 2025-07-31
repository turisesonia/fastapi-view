from unittest.mock import Mock

import pytest
from fastapi import Request

from fastapi_view.inertia.enums import InertiaHeader
from fastapi_view.inertia.inertia import Inertia
from fastapi_view.view import View


@pytest.fixture
def mock_view():
    """建立 mock View 物件"""
    view = Mock(spec=View)
    view.request = Mock(spec=Request)
    view.request.headers = {}
    view.request.url = "http://test.com/"
    view.render = Mock(return_value="mocked_response")
    return view


def test_inertia_init(mock_view):
    """測試 Inertia 初始化"""
    inertia = Inertia(view=mock_view, root_template="test.html")
    assert inertia.view == mock_view
    assert inertia.root_template == "test.html"


def test_inertia_header():
    assert {InertiaHeader.X_INERTIA: "XX"} == {"X-Inertia": "XX"}


def test_resolve_prop_callables_flat_structure(mock_view):
    inertia = Inertia(view=mock_view, root_template="test.html")

    def simple_callable():
        return "called_value"

    def get_user_count():
        return 42

    props = {
        "name": "John",
        "age": 30,
        "get_message": lambda: "Hello World",
        "user_count": get_user_count,
        "static_value": "unchanged",
        "number": 123,
        "boolean": True,
        "none_value": None,
        "list_value": [1, 2, 3],
        "callback": simple_callable,
    }

    result = inertia._resolve_prop_callables(props)

    assert result == {
        "name": "John",
        "age": 30,
        "get_message": "Hello World",
        "user_count": 42,
        "static_value": "unchanged",
        "number": 123,
        "boolean": True,
        "none_value": None,
        "list_value": [1, 2, 3],
        "callback": "called_value",
    }


def test_resolve_prop_callables_nested_structure(mock_view):
    inertia = Inertia(view=mock_view, root_template="test.html")

    def get_user_permissions():
        return ["read", "write", "admin"]

    def calculate_score():
        return 95.5

    def get_current_time():
        return "2024-07-31T10:30:00"

    class Counter:
        def __init__(self):
            self.count = 0

        def __call__(self):
            self.count += 1
            return self.count

    counter = Counter()

    props_nested = {
        "user": {
            "id": 1,
            "name": "Alice",
            "permissions": get_user_permissions,
            "profile": {
                "score": calculate_score,
                "last_login": get_current_time,
                "settings": {
                    "theme": "dark",
                    "notifications": lambda: True,
                    "counter": counter,
                },
            },
        },
        "metadata": {
            "version": "1.0",
            "timestamp": lambda: "2024-07-31",
            "config": {"debug": False, "log_level": lambda: "INFO"},
        },
        "static_data": "unchanged",
        "dynamic_value": lambda: "generated",
    }

    result = inertia._resolve_prop_callables(props_nested)

    assert result == {
        "user": {
            "id": 1,
            "name": "Alice",
            "permissions": ["read", "write", "admin"],
            "profile": {
                "score": 95.5,
                "last_login": "2024-07-31T10:30:00",
                "settings": {"theme": "dark", "notifications": True, "counter": 1},
            },
        },
        "metadata": {
            "version": "1.0",
            "timestamp": "2024-07-31",
            "config": {"debug": False, "log_level": "INFO"},
        },
        "static_data": "unchanged",
        "dynamic_value": "generated",
    }


def test_resolve_prop_callables_no_callables(mock_view):
    inertia = Inertia(view=mock_view, root_template="test.html")

    props = {
        "name": "John",
        "age": 30,
        "nested": {
            "value": "test",
            "number": 42,
        },
    }

    result = inertia._resolve_prop_callables(props)

    assert result == props


def test_resolve_prop_callables_empty_dict(mock_view):
    inertia = Inertia(view=mock_view, root_template="test.html")

    assert inertia._resolve_prop_callables({}) == {}


def test_build_page_props_basic(mock_view):
    """測試 _build_page_props 基本功能"""
    inertia = Inertia(view=mock_view, root_template="test.html", assets_version="v1.0")

    props = {
        "name": "John",
        "age": 30,
        "callback": lambda: "called_value",
    }

    result = inertia._build_page_props("TestComponent", mock_view.request, props)

    assert result["version"] == "v1.0"
    assert result["component"] == "TestComponent"
    assert result["url"] == "http://test.com/"
    assert result["props"] == {
        "name": "John",
        "age": 30,
        "callback": "called_value",
    }


def test_build_page_props_with_shared_props(mock_view):
    """測試 _build_page_props 包含共享屬性"""
    inertia = Inertia(view=mock_view, root_template="test.html", assets_version="v1.0")
    inertia._share = {"global_data": "shared_value", "app_name": "TestApp"}

    props = {
        "name": "John",
        "age": 30,
        "callback": lambda: "called_value",
    }

    result = inertia._build_page_props("TestComponent", mock_view.request, props)

    assert result["props"] == {
        "global_data": "shared_value",
        "app_name": "TestApp",
        "name": "John",
        "age": 30,
        "callback": "called_value",
    }

    inertia._share.clear()


def test_build_page_props_partial_request(mock_view):
    """測試 _build_page_props 部分請求"""
    mock_view.request.headers = {
        InertiaHeader.X_INERTIA_PARTIAL_DATA: "user, metadata",
        InertiaHeader.X_INERTIA_PARTIAL_COMPONENT: "TestComponent",
    }

    inertia = Inertia(view=mock_view, root_template="test.html")

    props = {
        "user": "Alice",
        "metadata": "v1.0",
        "static_data": "unchanged",
        "dynamic_value": "generated",
    }

    result = inertia._build_page_props("TestComponent", mock_view.request, props)

    assert result["props"] == {
        "user": "Alice",
        "metadata": "v1.0",
    }


def test_build_page_props_lazy_props_excluded(mock_view):
    """測試 _build_page_props 非部分請求時排除 LazyProp"""
    from fastapi_view.inertia.inertia import LazyProp

    inertia = Inertia(view=mock_view, root_template="test.html")

    props = {
        "name": "John",
        "age": 30,
        "callback": lambda: "called_value",
        "lazy_prop": LazyProp(lambda: "lazy_value"),
    }

    result = inertia._build_page_props("TestComponent", mock_view.request, props)

    assert "lazy_prop" not in result["props"]
    assert result["props"] == {
        "name": "John",
        "age": 30,
        "callback": "called_value",
    }
