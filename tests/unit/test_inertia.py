from unittest.mock import Mock

import pytest
from fastapi import Request
from fastapi.templating import Jinja2Templates

from fastapi_view.inertia import Inertia, InertiaConfig
from fastapi_view.inertia.enums import InertiaHeader
from fastapi_view.inertia.props import IgnoreFirstLoad, OptionalProp
from fastapi_view.view import View


@pytest.fixture
def mock_request():
    """建立 mock Request 物件"""
    request = Mock(spec=Request)
    request.headers = {}
    request.url = "http://test.com/"
    return request


@pytest.fixture
def inertia_config() -> InertiaConfig:
    return InertiaConfig(
        root_template="app.html",
        assets_version="1.0.0",
    )


@pytest.fixture
def inertia(mock_request, inertia_config) -> Inertia:
    return Inertia(
        request=mock_request,
        templates=Jinja2Templates(directory="templates"),
        config=inertia_config,
    )


def test_inertia_init(mock_request, inertia_config: InertiaConfig):
    inertia = Inertia(
        request=mock_request,
        templates=Jinja2Templates(directory="templates"),
        config=inertia_config,
    )
    assert isinstance(inertia._view, View)
    assert inertia._root_template == "app.html"


def test_is_partial_request(mock_request, inertia: Inertia):
    """測試 _is_partial_request 屬性的各種情況"""

    # 沒有 partial headers 時為 False
    assert inertia._is_partial_request is False

    # 有 headers 但 component 未設置時為 False
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "name,age"
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    assert inertia._is_partial_request is False

    # component 不匹配時為 False
    inertia._component = "DifferentComponent"
    assert inertia._is_partial_request is False

    # headers 和 component 匹配時為 True
    inertia._component = "TestComponent"
    assert inertia._is_partial_request is True


def test_partial_only_keys(mock_request, inertia: Inertia):
    """測試 _partial_only_keys 屬性的各種情況"""

    # 沒有 header 時返回空字串列表
    assert inertia._partial_only_keys == [""]

    # 單一 key
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "name"
    assert inertia._partial_only_keys == ["name"]

    # 多個 keys 且包含空格
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "name, age , email"
    assert inertia._partial_only_keys == ["name", "age", "email"]


def test_partial_except_keys(mock_request, inertia: Inertia):
    """測試 _partial_except_keys 屬性的各種情況"""

    # 沒有 header 時返回空字串列表
    assert inertia._partial_except_keys == [""]

    # 單一 key
    mock_request.headers[InertiaHeader.PARTIAL_EXCEPT] = "password"
    assert inertia._partial_except_keys == ["password"]

    # 多個 keys 且包含空格
    mock_request.headers[InertiaHeader.PARTIAL_EXCEPT] = "password, secret , token"
    assert inertia._partial_except_keys == ["password", "secret", "token"]


def test_resolve_partial_props_non_partial_request(inertia: Inertia):
    """測試 _resolve_partial_props 非 partial request 的情況"""
    # 普通 props，無 IgnoreFirstLoad
    props_normal = {"name": "John", "age": 30, "email": "john@example.com"}
    result = inertia._resolve_partial_props(props_normal)
    assert result == {"name": "John", "age": 30, "email": "john@example.com"}

    # 包含 IgnoreFirstLoad props
    props_with_ignore = {
        "name": "John",
        "age": 30,
        "lazy_data": IgnoreFirstLoad(),
        "optional_data": OptionalProp("optional_value"),
    }
    result = inertia._resolve_partial_props(props_with_ignore)
    assert result == {"name": "John", "age": 30}

    # 全部都是 IgnoreFirstLoad
    props_all_ignore = {"lazy1": IgnoreFirstLoad(), "lazy2": OptionalProp("value")}
    result = inertia._resolve_partial_props(props_all_ignore)
    assert result == {}


def test_resolve_partial_props_basic_partial_request(mock_request, inertia: Inertia):
    """測試 _resolve_partial_props 基本 partial request"""
    # 設置 partial request
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "name,age"
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    inertia._component = "TestComponent"

    props = {
        "name": "John",
        "age": 30,
        "email": "john@example.com",
        "password": "secret",
    }
    result = inertia._resolve_partial_props(props)
    assert result == {"name": "John", "age": 30}


def test_resolve_partial_props_with_except_keys(mock_request, inertia: Inertia):
    """測試 _resolve_partial_props 有 except keys 的 partial request"""
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "name,age,password"
    mock_request.headers[InertiaHeader.PARTIAL_EXCEPT] = "password"
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    inertia._component = "TestComponent"

    props = {
        "name": "John",
        "age": 30,
        "email": "john@example.com",
        "password": "secret",
    }
    result = inertia._resolve_partial_props(props)
    assert result == {"name": "John", "age": 30}


def test_resolve_partial_props_no_matching_keys(mock_request, inertia: Inertia):
    """測試 _resolve_partial_props partial_only_keys 無匹配的情況"""
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "nonexistent"
    mock_request.headers[InertiaHeader.PARTIAL_EXCEPT] = ""
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    inertia._component = "TestComponent"

    props = {"name": "John", "age": 30}
    result = inertia._resolve_partial_props(props)
    assert result == {}


def test_resolve_partial_props_ignore_first_load_in_partial(
    mock_request, inertia: Inertia
):
    """測試 _resolve_partial_props 在 partial request 中 IgnoreFirstLoad 不會被過濾"""
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "name,lazy_data"
    mock_request.headers[InertiaHeader.PARTIAL_EXCEPT] = ""
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    inertia._component = "TestComponent"

    props = {
        "name": "John",
        "age": 30,
        "lazy_data": IgnoreFirstLoad(),
        "email": "john@example.com",
    }
    result = inertia._resolve_partial_props(props)
    assert result == {
        "name": "John",
        "lazy_data": props["lazy_data"],  # 保持原物件引用
    }


def test_resolve_callable_props_basic_functions(inertia: Inertia):
    """測試 _resolve_callable_props 處理基本函數"""

    def simple_function():
        return "function_result"

    props = {
        "name": "John",
        "age": 30,
        "message": lambda: "Hello World",
        "count": simple_function,
        "static": "unchanged",
    }
    result = inertia._resolve_callable_props(props)
    assert result == {
        "name": "John",
        "age": 30,
        "message": "Hello World",
        "count": "function_result",
        "static": "unchanged",
    }


def test_resolve_callable_props_callable_objects(inertia: Inertia):
    """測試 _resolve_callable_props 處理可呼叫物件"""

    class Counter:
        def __init__(self):
            self.count = 0

        def __call__(self):
            self.count += 1
            return self.count

    counter = Counter()
    props = {"counter": counter, "name": "test"}
    result = inertia._resolve_callable_props(props)
    assert result == {"counter": 1, "name": "test"}

    # 驗證方法會修改原始字典（callable 被結果替換）
    assert props["counter"] == 1  # 原字典已被修改
    assert props["name"] == "test"  # 非 callable 值保持不變


def test_resolve_callable_props_nested_dicts(inertia: Inertia):
    """測試 _resolve_callable_props 處理巢狀字典"""
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


def test_resolve_callable_props_deep_nested_dicts(inertia: Inertia):
    """測試 _resolve_callable_props 處理深層巢狀字典"""
    props = {
        "level1": {
            "level2": {
                "level3": {"deep_func": lambda: "deep_result", "value": "static"},
                "mid_func": lambda: "mid_result",
            },
            "top_func": lambda: "top_result",
        }
    }
    result = inertia._resolve_callable_props(props)
    assert result == {
        "level1": {
            "level2": {
                "level3": {"deep_func": "deep_result", "value": "static"},
                "mid_func": "mid_result",
            },
            "top_func": "top_result",
        }
    }


def test_resolve_callable_props_edge_cases(inertia: Inertia):
    """測試 _resolve_callable_props 邊界情況"""
    # 空字典
    props_empty = {}
    result = inertia._resolve_callable_props(props_empty)
    assert result == {}

    # 非字典類型不應被遞歸處理
    props_non_dict = {
        "list_data": [lambda: "should_not_call", "static"],
        "tuple_data": (lambda: "should_not_call", "static"),
        "string_data": "normal_string",
        "none_data": None,
    }
    original_list = props_non_dict["list_data"][:]
    original_tuple = props_non_dict["tuple_data"]

    result = inertia._resolve_callable_props(props_non_dict)
    assert result == {
        "list_data": original_list,  # 列表內的 lambda 不應被呼叫
        "tuple_data": original_tuple,  # 元組內的 lambda 不應被呼叫
        "string_data": "normal_string",
        "none_data": None,
    }


def test_resolve_callable_props_complex_returns(inertia: Inertia):
    """測試 _resolve_callable_props 處理返回複雜物件的函數"""

    def get_user_data():
        return {"id": 1, "name": "Bob", "permissions": ["admin"]}

    props = {"user_data": get_user_data, "timestamp": lambda: "2024-08-04"}
    result = inertia._resolve_callable_props(props)
    assert result == {
        "user_data": {"id": 1, "name": "Bob", "permissions": ["admin"]},
        "timestamp": "2024-08-04",
    }


def test_resolve_callable_props_no_recursive_on_returned_dicts(inertia: Inertia):
    """測試 _resolve_callable_props 不會對返回的字典進行遞歸處理"""

    def get_dict_with_callable():
        return {"nested_func": lambda: "this_should_not_be_called", "value": "static"}

    props = {"data": get_dict_with_callable}
    result = inertia._resolve_callable_props(props)
    returned_dict = result["data"]

    # 確認返回的字典內的 lambda 沒有被呼叫
    assert callable(returned_dict["nested_func"])
    assert returned_dict["value"] == "static"
