from unittest.mock import Mock, patch

import pytest
from fastapi import Request

from fastapi_view.inertia import Inertia
from fastapi_view.inertia.enums import InertiaHeader
from fastapi_view.inertia.inertia import FLASH_PROPS_KEY, REQUEST_SESSION_KEY
from fastapi_view.inertia.props import MergeProp
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
    # Clear shared state before each test
    Inertia._share = {}

    with patch("fastapi_view.inertia.inertia.ViewContext") as mock_view_cls:
        mock_view_cls.return_value = mock_view_instance

        inertia = Inertia(mock_request)

        return inertia


# ============================================================================
# MergeProp Class Tests
# ============================================================================


def test_merge_prop_basic_configuration():
    """Test basic MergeProp configuration"""
    merge_prop = MergeProp(lambda: ["item1", "item2"])

    assert merge_prop.should_merge() is True
    assert merge_prop.should_deep_merge() is False
    assert merge_prop.appends_at_root() is True
    assert merge_prop.prepends_at_root() is False


def test_merge_prop_deep_merge():
    """Test deep merge configuration"""
    merge_prop = MergeProp(lambda: {"key": "value"}).deep_merge()

    assert merge_prop.should_merge() is True
    assert merge_prop.should_deep_merge() is True


def test_merge_prop_prepend():
    """Test prepend configuration"""
    merge_prop = MergeProp(lambda: ["new"]).prepend()

    assert merge_prop.appends_at_root() is False
    assert merge_prop.prepends_at_root() is True


def test_merge_prop_append_with_path():
    """Test append at specific path"""
    merge_prop = MergeProp(lambda: []).append("data")

    assert merge_prop.appends_at_root() is False
    assert "data" in merge_prop.appends_at_paths()


def test_merge_prop_prepend_with_path():
    """Test prepend at specific path"""
    merge_prop = MergeProp(lambda: []).prepend("messages")

    assert merge_prop.prepends_at_root() is False
    assert "messages" in merge_prop.prepends_at_paths()


def test_merge_prop_match_on():
    """Test match on configuration"""
    merge_prop = MergeProp(lambda: []).append(match_on="id")

    assert "id" in merge_prop.matches_on()


def test_merge_prop_multiple_paths():
    """Test multiple path configuration"""
    merge_prop = MergeProp(lambda: []).append(["data", "items"])

    assert "data" in merge_prop.appends_at_paths()
    assert "items" in merge_prop.appends_at_paths()


def test_merge_prop_callable_resolution():
    """Test MergeProp resolves callable values"""
    merge_prop = MergeProp(lambda: [{"id": 1, "name": "Test"}])

    result = merge_prop()

    assert result == [{"id": 1, "name": "Test"}]


def test_merge_prop_non_callable_resolution():
    """Test MergeProp resolves non-callable values"""
    data = [{"id": 1, "name": "Test"}]
    merge_prop = MergeProp(data)

    result = merge_prop()

    assert result == data


# ============================================================================
# Initial Load Tests
# ============================================================================


def test_merge_props_excluded_on_initial_load(inertia):
    """Test merge props are excluded from initial load"""
    inertia._component = "TestComponent"
    props = {
        "users": [{"id": 1, "name": "John"}],
        "posts": MergeProp(lambda: [{"id": 1, "title": "Post 1"}]),
    }

    result = inertia._build_page_object(props)

    # Merge prop should NOT be in resolved props
    assert "posts" not in result["props"]
    assert "users" in result["props"]

    # Merge config should be present
    assert "mergeProps" in result
    assert "posts" in result["mergeProps"]


def test_merge_props_with_prepend_config(inertia):
    """Test prepend props configuration"""
    inertia._component = "TestComponent"
    props = {
        "notifications": MergeProp(lambda: []).prepend(),
    }

    result = inertia._build_page_object(props)

    assert "prependProps" in result
    assert "notifications" in result["prependProps"]


def test_merge_props_with_deep_merge_config(inertia):
    """Test deep merge configuration"""
    inertia._component = "TestComponent"
    props = {
        "settings": MergeProp(lambda: {}).deep_merge(),
    }

    result = inertia._build_page_object(props)

    assert "deepMergeProps" in result
    assert "settings" in result["deepMergeProps"]


def test_merge_props_with_match_on_config(inertia):
    """Test match on configuration"""
    inertia._component = "TestComponent"
    props = {
        "users": MergeProp(lambda: []).append(match_on="id"),
    }

    result = inertia._build_page_object(props)

    assert "matchPropsOn" in result
    assert result["matchPropsOn"]["users"] == "id"


def test_merge_props_multiple_configurations(inertia):
    """Test multiple merge configurations in one response"""
    inertia._component = "TestComponent"
    props = {
        "users": MergeProp(lambda: []).append(match_on="id"),
        "notifications": MergeProp(lambda: []).prepend(),
        "settings": MergeProp(lambda: {}).deep_merge(),
        "posts": MergeProp(lambda: []),
    }

    result = inertia._build_page_object(props)

    # All merge props should be in mergeProps list
    assert "mergeProps" in result
    assert len(result["mergeProps"]) == 4
    assert "users" in result["mergeProps"]
    assert "notifications" in result["mergeProps"]
    assert "settings" in result["mergeProps"]
    assert "posts" in result["mergeProps"]

    # Prepend config
    assert "prependProps" in result
    assert "notifications" in result["prependProps"]

    # Deep merge config
    assert "deepMergeProps" in result
    assert "settings" in result["deepMergeProps"]

    # Match on config
    assert "matchPropsOn" in result
    assert result["matchPropsOn"]["users"] == "id"


def test_merge_props_no_config_when_none_present(inertia):
    """Test no merge config is added when no merge props present"""
    inertia._component = "TestComponent"
    props = {
        "users": [{"id": 1, "name": "John"}],
        "count": 42,
    }

    result = inertia._build_page_object(props)

    # No merge config keys should be present
    assert "mergeProps" not in result
    assert "prependProps" not in result
    assert "deepMergeProps" not in result
    assert "matchPropsOn" not in result


# ============================================================================
# Partial Request Tests
# ============================================================================


def test_merge_props_resolved_on_partial_request(mock_request, inertia):
    """Test merge props are resolved during partial request"""
    # Setup partial request
    mock_request.headers[InertiaHeader.INERTIA] = "true"
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "posts"
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    inertia._component = "TestComponent"

    props = {
        "users": [{"id": 1}],
        "posts": MergeProp(lambda: [{"id": 2, "title": "Post 2"}]),
    }

    result = inertia._build_page_object(props)

    # Only requested merge prop should be resolved
    assert "posts" in result["props"]
    assert result["props"]["posts"] == [{"id": 2, "title": "Post 2"}]
    assert "users" not in result["props"]

    # Merge config SHOULD be present for partial requests
    # The client needs this metadata to know how to merge the props
    assert "mergeProps" in result
    assert "posts" in result["mergeProps"]


def test_merge_props_partial_request_multiple_props(mock_request, inertia):
    """Test multiple merge props resolved during partial request"""
    # Setup partial request
    mock_request.headers[InertiaHeader.INERTIA] = "true"
    mock_request.headers[InertiaHeader.PARTIAL_ONLY] = "posts,users"
    mock_request.headers[InertiaHeader.PARTIAL_COMPONENT] = "TestComponent"
    inertia._component = "TestComponent"

    props = {
        "posts": MergeProp(lambda: [{"id": 1}]),
        "users": MergeProp(lambda: [{"id": 2}]),
        "comments": MergeProp(lambda: [{"id": 3}]),
    }

    result = inertia._build_page_object(props)

    # Only requested props should be resolved
    assert "posts" in result["props"]
    assert "users" in result["props"]
    assert "comments" not in result["props"]


# ============================================================================
# Helper Methods Tests
# ============================================================================


def test_inertia_merge_helper_method():
    """Test Inertia.merge() helper method"""
    merge_prop = Inertia.merge(lambda: ["data"])

    assert isinstance(merge_prop, MergeProp)
    assert merge_prop.should_merge() is True
    assert merge_prop() == ["data"]


def test_inertia_deep_merge_helper_method():
    """Test Inertia.deep_merge() helper method"""
    merge_prop = Inertia.deep_merge(lambda: {"key": "value"})

    assert isinstance(merge_prop, MergeProp)
    assert merge_prop.should_deep_merge() is True
    assert merge_prop() == {"key": "value"}


def test_inertia_merge_with_fluent_interface():
    """Test Inertia.merge() with fluent interface"""
    merge_prop = Inertia.merge(lambda: []).append("data", match_on="id")

    assert isinstance(merge_prop, MergeProp)
    assert "data" in merge_prop.appends_at_paths()
    assert "id" in merge_prop.matches_on()


# ============================================================================
# Integration with Other Features
# ============================================================================


def test_merge_props_combined_with_deferred_props(inertia):
    """Test merge props can coexist with deferred props"""
    from fastapi_view.inertia.props import DeferredProp

    inertia._component = "TestComponent"
    props = {
        "quick": {"name": "Fast data"},
        "slow": DeferredProp(lambda: {"name": "Slow data"}, group="lazy"),
        "paginated": MergeProp(lambda: [1, 2, 3]),
    }

    result = inertia._build_page_object(props)

    # Both configs should coexist
    assert "deferredProps" in result
    assert "mergeProps" in result
    assert "slow" in result["deferredProps"]["lazy"]
    assert "paginated" in result["mergeProps"]


def test_merge_props_mixed_with_regular_props(inertia):
    """Test merge props work alongside regular props"""
    inertia._component = "TestComponent"
    props = {
        "user": {"id": 1, "name": "John"},
        "posts": MergeProp(lambda: [{"id": 1}]),
        "count": 42,
    }

    result = inertia._build_page_object(props)

    # Regular props should be included
    assert result["props"]["user"] == {"id": 1, "name": "John"}
    assert result["props"]["count"] == 42

    # Merge prop should be excluded but configured
    assert "posts" not in result["props"]
    assert "posts" in result["mergeProps"]


def test_merge_props_with_shared_props(inertia):
    """Test merge props work with shared props"""
    inertia._component = "TestComponent"
    inertia.share("auth", {"user": {"id": 1}})

    props = {
        "posts": MergeProp(lambda: [{"id": 1}]),
    }

    result = inertia._build_page_object(props)

    # Shared props should be included
    assert "auth" in result["props"]
    assert result["props"]["auth"] == {"user": {"id": 1}}

    # Merge prop should be excluded but configured
    assert "posts" not in result["props"]
    assert "posts" in result["mergeProps"]


# ============================================================================
# Edge Cases
# ============================================================================


def test_merge_prop_with_empty_list(inertia):
    """Test merge prop with empty list"""
    inertia._component = "TestComponent"
    props = {
        "items": MergeProp(lambda: []),
    }

    result = inertia._build_page_object(props)

    assert "mergeProps" in result
    assert "items" in result["mergeProps"]


def test_merge_prop_with_none_value(inertia):
    """Test merge prop with None value"""
    inertia._component = "TestComponent"
    props = {
        "data": MergeProp(lambda: None),
    }

    result = inertia._build_page_object(props)

    assert "mergeProps" in result
    assert "data" in result["mergeProps"]


def test_merge_prop_append_and_prepend_false(inertia):
    """Test merge prop with both append and prepend set to False"""
    inertia._component = "TestComponent"

    # Create a merge prop and set both to False via paths
    merge_prop = MergeProp(lambda: [])
    merge_prop.append(False)
    merge_prop.prepend(False)

    props = {
        "items": merge_prop,
    }

    result = inertia._build_page_object(props)

    # Should still be in mergeProps
    assert "mergeProps" in result
    assert "items" in result["mergeProps"]

    # Should not be in prependProps (prepend was set to False)
    assert "prependProps" not in result


def test_merge_prop_multiple_match_on_fields(inertia):
    """Test merge prop with multiple match_on calls"""
    inertia._component = "TestComponent"

    merge_prop = MergeProp(lambda: [])
    merge_prop.append(match_on="id")
    merge_prop.append(match_on="slug")

    props = {
        "items": merge_prop,
    }

    result = inertia._build_page_object(props)

    # Should use first match field (Laravel behavior)
    assert "matchPropsOn" in result
    assert result["matchPropsOn"]["items"] == "id"


def test_merge_prop_chained_configuration(inertia):
    """Test merge prop with chained configuration"""
    inertia._component = "TestComponent"

    merge_prop = Inertia.merge(lambda: []).deep_merge().append("data", match_on="id")

    props = {
        "items": merge_prop,
    }

    result = inertia._build_page_object(props)

    assert "mergeProps" in result
    assert "deepMergeProps" in result
    assert "matchPropsOn" in result
    assert result["matchPropsOn"]["items"] == "id"


# ============================================================================
# Flash Messages Integration
# ============================================================================


def test_merge_props_with_flash_messages(inertia, mock_request):
    """Test merge props work with flash messages"""
    # Setup session with flash messages
    mock_request.session = {"flash": {"success": "Data saved"}}
    mock_request.scope[REQUEST_SESSION_KEY] = mock_request.session

    inertia._component = "TestComponent"
    props = {
        "posts": MergeProp(lambda: [{"id": 1}]),
    }

    result = inertia._build_page_object(props)

    # Flash messages should be included
    assert FLASH_PROPS_KEY in result["props"]
    assert result["props"][FLASH_PROPS_KEY] == {"success": "Data saved"}

    # Merge prop should be configured
    assert "mergeProps" in result
    assert "posts" in result["mergeProps"]
