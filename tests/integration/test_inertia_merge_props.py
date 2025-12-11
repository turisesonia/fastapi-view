import json
from datetime import datetime
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from pyquery import PyQuery as pq

from fastapi_view.inertia import Inertia, InertiaDepends
from fastapi_view.inertia.enums import InertiaHeader


class Post(BaseModel):
    id: int
    title: str
    created_at: datetime = datetime.now()


class User(BaseModel):
    id: int
    name: str
    email: str


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables"""
    templates_path = Path("tests/templates").resolve()
    monkeypatch.setenv("FV_TEMPLATES_PATH", str(templates_path))
    monkeypatch.setenv("FV_INERTIA_ROOT_TEMPLATE", "inertia.html")
    monkeypatch.setenv("FV_INERTIA_ASSETS_VERSION", "1.0.0")
    monkeypatch.setenv("FV_VITE_DEV_MODE", "true")


@pytest.fixture
def app() -> FastAPI:
    """Create FastAPI app with merge props endpoints"""
    app = FastAPI(title="Merge Props Integration Test App")

    # Sample data
    ALL_POSTS = [Post(id=i, title=f"Post {i}") for i in range(1, 51)]

    ALL_USERS = [
        User(id=i, name=f"User{i}", email=f"user{i}@example.com") for i in range(1, 31)
    ]

    @app.get("/posts")
    def list_posts(inertia: InertiaDepends, page: int = 1, per_page: int = 10):
        """Paginated posts list with merge props for "Load More" functionality"""
        offset = (page - 1) * per_page
        posts = ALL_POSTS[offset : offset + per_page]

        return inertia.render(
            "Posts/Index",
            {
                "posts": inertia.merge(lambda: posts),
                "has_more": len(ALL_POSTS) > offset + per_page,
                "page": page,
                "total": len(ALL_POSTS),
            },
        )

    @app.get("/posts/prepend")
    def posts_prepend(inertia: InertiaDepends, latest_id: int = 0):
        """New posts prepended to list"""
        # Simulate new posts created after latest_id
        new_posts = [Post(id=100 + i, title=f"New Post {100 + i}") for i in range(1, 4)]

        return inertia.render(
            "Posts/Prepend",
            {
                "posts": inertia.merge(lambda: new_posts).prepend(),
                "latest_id": 103,
            },
        )

    @app.get("/posts/with-match")
    def posts_with_match(inertia: InertiaDepends, page: int = 1):
        """Posts with match on ID to update existing items"""
        offset = (page - 1) * 10
        posts = ALL_POSTS[offset : offset + 10]

        return inertia.render(
            "Posts/Match",
            {
                "posts": inertia.merge(lambda: posts).append(match_on="id"),
                "page": page,
            },
        )

    @app.get("/users/nested")
    def users_nested(inertia: InertiaDepends, page: int = 1):
        """Users with nested data structure"""
        offset = (page - 1) * 10
        users = ALL_USERS[offset : offset + 10]

        return inertia.render(
            "Users/Nested",
            {
                "pagination": {
                    "data": inertia.merge(lambda: users).append("data", match_on="id"),
                    "page": page,
                    "per_page": 10,
                },
            },
        )

    @app.get("/settings")
    def settings(inertia: InertiaDepends):
        """Settings with deep merge"""
        settings_update = {
            "theme": {
                "color": "blue",
                "mode": "dark",
            },
            "notifications": {
                "email": True,
            },
        }

        return inertia.render(
            "Settings/Index",
            {
                "settings": inertia.deep_merge(lambda: settings_update),
            },
        )

    @app.get("/mixed")
    def mixed_props(inertia: InertiaDepends, page: int = 1):
        """Mix of regular, deferred, and merge props"""
        offset = (page - 1) * 10
        posts = ALL_POSTS[offset : offset + 10]

        return inertia.render(
            "Mixed",
            {
                "user": {"id": 1, "name": "John"},
                "posts": inertia.merge(lambda: posts).append(match_on="id"),
                "stats": inertia.defer(
                    lambda: {"views": 1000, "likes": 50}, group="analytics"
                ),
                "page": page,
            },
        )

    @app.get("/multiple-merge")
    def multiple_merge(inertia: InertiaDepends):
        """Multiple merge props with different configurations"""
        return inertia.render(
            "MultipleMerge",
            {
                "posts": inertia.merge(lambda: ALL_POSTS[:5]),
                "users": inertia.merge(lambda: ALL_USERS[:5]).prepend(),
                "settings": inertia.deep_merge(lambda: {"theme": "dark"}),
                "notifications": inertia.merge(lambda: [{"id": 1}]).append(
                    match_on="id"
                ),
            },
        )

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create TestClient for FastAPI app"""
    return TestClient(app)


# ============================================================================
# Initial Load Tests
# ============================================================================


def test_merge_props_initial_load_excludes_merge_props(client: TestClient):
    """Test initial load excludes merge props from response"""
    response = client.get("/posts")

    assert response.status_code == 200

    # Parse HTML using pyquery
    d = pq(response.text)
    app_div = d("#app")
    page_data = json.loads(app_div.attr("data-page"))

    # Merge prop should NOT be in props
    assert "posts" not in page_data["props"]

    # Merge config should be present
    assert "mergeProps" in page_data
    assert "posts" in page_data["mergeProps"]

    # Regular props should be present
    assert "has_more" in page_data["props"]
    assert "page" in page_data["props"]


def test_merge_props_prepend_configuration(client: TestClient):
    """Test prepend merge configuration"""
    response = client.get("/posts/prepend")

    assert response.status_code == 200

    d = pq(response.text)
    app_div = d("#app")
    page_data = json.loads(app_div.attr("data-page"))

    # Prepend config should be present
    assert "prependProps" in page_data
    assert "posts" in page_data["prependProps"]


def test_merge_props_match_on_configuration(client: TestClient):
    """Test match on configuration"""
    response = client.get("/posts/with-match")

    assert response.status_code == 200

    d = pq(response.text)
    app_div = d("#app")
    page_data = json.loads(app_div.attr("data-page"))

    # Match on config should be present
    assert "matchPropsOn" in page_data
    assert page_data["matchPropsOn"]["posts"] == "id"


def test_merge_props_deep_merge_configuration(client: TestClient):
    """Test deep merge configuration"""
    response = client.get("/settings")

    assert response.status_code == 200

    d = pq(response.text)
    app_div = d("#app")
    page_data = json.loads(app_div.attr("data-page"))

    # Deep merge config should be present
    assert "deepMergeProps" in page_data
    assert "settings" in page_data["deepMergeProps"]


def test_merge_props_multiple_configurations(client: TestClient):
    """Test multiple merge configurations in one response"""
    response = client.get("/multiple-merge")

    assert response.status_code == 200

    d = pq(response.text)
    app_div = d("#app")
    page_data = json.loads(app_div.attr("data-page"))

    # All merge configs should be present
    assert "mergeProps" in page_data
    assert len(page_data["mergeProps"]) == 4

    assert "prependProps" in page_data
    assert "users" in page_data["prependProps"]

    assert "deepMergeProps" in page_data
    assert "settings" in page_data["deepMergeProps"]

    assert "matchPropsOn" in page_data
    assert page_data["matchPropsOn"]["notifications"] == "id"


# ============================================================================
# Partial Request Tests
# ============================================================================


def test_merge_props_partial_request_resolves_merge_props(client: TestClient):
    """Test partial request resolves merge props"""
    response = client.get(
        "/posts?page=2",
        headers={
            InertiaHeader.INERTIA: "true",
            InertiaHeader.PARTIAL_ONLY: "posts",
            InertiaHeader.PARTIAL_COMPONENT: "Posts/Index",
        },
    )

    assert response.status_code == 200

    page_data = response.json()

    # Merge prop should be resolved
    assert "posts" in page_data["props"]
    assert isinstance(page_data["props"]["posts"], list)
    assert len(page_data["props"]["posts"]) == 10

    # First post should be from page 2 (id 11-20)
    assert page_data["props"]["posts"][0]["id"] == 11

    # Merge config SHOULD be present for partial requests
    # The client needs this metadata to know how to merge the props
    assert "mergeProps" in page_data
    assert "posts" in page_data["mergeProps"]


def test_merge_props_partial_request_with_prepend(client: TestClient):
    """Test partial request with prepend merge prop"""
    response = client.get(
        "/posts/prepend?latest_id=100",
        headers={
            InertiaHeader.INERTIA: "true",
            InertiaHeader.PARTIAL_ONLY: "posts",
            InertiaHeader.PARTIAL_COMPONENT: "Posts/Prepend",
        },
    )

    assert response.status_code == 200

    page_data = response.json()

    # Merge prop should be resolved
    assert "posts" in page_data["props"]
    assert len(page_data["props"]["posts"]) == 3

    # Posts should be new ones (id 101-103)
    assert page_data["props"]["posts"][0]["id"] == 101


def test_merge_props_partial_request_multiple_props(client: TestClient):
    """Test partial request with multiple merge props"""
    response = client.get(
        "/multiple-merge",
        headers={
            InertiaHeader.INERTIA: "true",
            InertiaHeader.PARTIAL_ONLY: "posts,users",
            InertiaHeader.PARTIAL_COMPONENT: "MultipleMerge",
        },
    )

    assert response.status_code == 200

    page_data = response.json()

    # Both requested merge props should be resolved
    assert "posts" in page_data["props"]
    assert "users" in page_data["props"]

    # Non-requested props should not be present
    assert "settings" not in page_data["props"]
    assert "notifications" not in page_data["props"]


# ============================================================================
# Integration with Other Features
# ============================================================================


def test_merge_props_with_deferred_props(client: TestClient):
    """Test merge props work with deferred props"""
    # Initial load
    response = client.get("/mixed")

    assert response.status_code == 200

    d = pq(response.text)
    app_div = d("#app")
    page_data = json.loads(app_div.attr("data-page"))

    # Both configs should be present
    assert "mergeProps" in page_data
    assert "deferredProps" in page_data

    assert "posts" in page_data["mergeProps"]
    assert "stats" in page_data["deferredProps"]["analytics"]


def test_merge_props_partial_request_with_deferred_props(client: TestClient):
    """Test partial request can fetch both merge and deferred props"""
    # Clear shared props to avoid pollution from other tests

    Inertia._share = {}

    response = client.get(
        "/mixed?page=2",
        headers={
            InertiaHeader.INERTIA: "true",
            InertiaHeader.PARTIAL_ONLY: "posts,stats",
            InertiaHeader.PARTIAL_COMPONENT: "Mixed",
        },
    )

    assert response.status_code == 200

    page_data = response.json()

    # Both merge and deferred props should be resolved
    assert "posts" in page_data["props"]
    assert "stats" in page_data["props"]

    # Regular props should not be present (not requested)
    assert "user" not in page_data["props"]


def test_merge_props_with_regular_props(client: TestClient):
    """Test merge props coexist with regular props"""
    response = client.get("/mixed")

    assert response.status_code == 200

    d = pq(response.text)
    app_div = d("#app")
    page_data = json.loads(app_div.attr("data-page"))

    # Regular props should be in response
    assert "user" in page_data["props"]
    assert page_data["props"]["user"]["name"] == "John"

    # Merge props should be configured
    assert "mergeProps" in page_data
    assert "posts" in page_data["mergeProps"]


# ============================================================================
# Edge Cases
# ============================================================================


def test_merge_props_pagination_scenario(client: TestClient):
    """Test realistic pagination scenario with merge props"""
    # Page 1 - Initial load
    response = client.get("/posts?page=1")
    assert response.status_code == 200

    d = pq(response.text)
    app_div = d("#app")
    page_data = json.loads(app_div.attr("data-page"))

    assert "mergeProps" in page_data
    assert page_data["props"]["page"] == 1
    assert page_data["props"]["has_more"] is True

    # Page 2 - Load more (partial request)
    response = client.get(
        "/posts?page=2",
        headers={
            InertiaHeader.INERTIA: "true",
            InertiaHeader.PARTIAL_ONLY: "posts",
            InertiaHeader.PARTIAL_COMPONENT: "Posts/Index",
        },
    )
    assert response.status_code == 200

    page_data = response.json()
    assert "posts" in page_data["props"]
    assert len(page_data["props"]["posts"]) == 10

    # Page 3 - Load more again
    response = client.get(
        "/posts?page=3",
        headers={
            InertiaHeader.INERTIA: "true",
            InertiaHeader.PARTIAL_ONLY: "posts",
            InertiaHeader.PARTIAL_COMPONENT: "Posts/Index",
        },
    )
    assert response.status_code == 200

    page_data = response.json()
    assert "posts" in page_data["props"]
    assert page_data["props"]["posts"][0]["id"] == 21  # Page 3 starts at id 21


def test_merge_props_nested_data_structure(client: TestClient):
    """Test merge props work with nested data structures"""
    response = client.get("/users/nested?page=1")

    assert response.status_code == 200

    d = pq(response.text)
    app_div = d("#app")
    page_data = json.loads(app_div.attr("data-page"))

    assert "pagination" in page_data["props"]


def test_merge_props_response_headers(client: TestClient):
    """Test merge props responses have correct headers"""
    # Partial request
    response = client.get(
        "/posts?page=2",
        headers={
            InertiaHeader.INERTIA: "true",
            InertiaHeader.PARTIAL_ONLY: "posts",
            InertiaHeader.PARTIAL_COMPONENT: "Posts/Index",
        },
    )

    assert response.status_code == 200
    assert response.headers[InertiaHeader.INERTIA] == "True"
    assert response.headers["Vary"] == "Accept"
