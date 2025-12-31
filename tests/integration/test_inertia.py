import json
from datetime import datetime
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from pyquery import PyQuery as pq
from starlette.middleware.sessions import SessionMiddleware

from fastapi_view.inertia import Inertia, InertiaDepends
from fastapi_view.inertia.enums import InertiaHeader
from fastapi_view.inertia.props import OptionalProp


class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime = datetime.now()


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
    app = FastAPI(title="Inertia Integration Test App")

    @app.get("/")
    def index(inertia: InertiaDepends, name: str = "World"):
        return inertia.render("Index", {"name": name, "message": "Welcome"})

    @app.get("/users")
    def list_users(inertia: InertiaDepends):
        users = [
            User(id=1, name="Alice", email="alice@example.com"),
            User(id=2, name="Bob", email="bob@example.com"),
            User(id=3, name="Charlie", email="charlie@example.com"),
        ]

        return inertia.render("UsersList", {"users": users})

    @app.get("/users/{user_id}")
    def user_detail(inertia: InertiaDepends, user_id: int):
        user = User(
            id=user_id,
            name=f"User{user_id}",
            email=f"user{user_id}@example.com",
        )

        return inertia.render("UserDetail", {"user": user})

    @app.get("/partial-demo")
    def partial_demo(inertia: InertiaDepends):
        return inertia.render(
            "PartialDemo",
            {
                "public_data": "Everyone can see this",
                "private_data": "Only partial requests see this",
                "lazy_data": OptionalProp(lambda: "Lazy loaded data"),
                "timestamp": lambda: datetime.now().isoformat(),
            },
        )

    @app.get("/shared-demo")
    def shared_demo(inertia: InertiaDepends):
        inertia.share("app_name", "Test App")
        inertia.share("user", {"name": "John", "role": "admin"})

        return inertia.render("SharedDemo", {"page_data": "Page specific data"})

    return app


def test_inertia_html_response(app):
    """Test normal HTTP request returns HTML"""

    with TestClient(app) as client:
        response = client.get("/", params={"name": "Alice"})

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "inertia.html"

        d = pq(response.text)
        app_div = d("#app")
        page_data = json.loads(app_div.attr("data-page"))

        assert page_data["component"] == "Index"
        assert page_data["props"]["flash"] == {}
        assert page_data["props"]["name"] == "Alice"
        assert page_data["props"]["message"] == "Welcome"
        assert page_data["version"] == "1.0.0"
        assert "url" in page_data


def test_inertia_json_response(app):
    """Test Inertia AJAX request returns JSON"""

    with TestClient(app) as client:
        response = client.get(
            "/", params={"name": "Bob"}, headers={InertiaHeader.INERTIA: "true"}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert response.headers[InertiaHeader.INERTIA] == "True"
        assert response.headers["vary"] == "Accept"

        data = response.json()
        assert data["component"] == "Index"
        assert data["props"]["flash"] == {}
        assert data["props"]["name"] == "Bob"
        assert data["props"]["message"] == "Welcome"
        assert data["version"] == "1.0.0"
        assert "url" in data


def test_inertia_page_data_structure(app):
    with TestClient(app) as client:
        response = client.get("/users", headers={InertiaHeader.INERTIA: "true"})

        data = response.json()

        assert "component" in data
        assert "props" in data
        assert "version" in data
        assert "url" in data

        assert "flash" in data["props"]
        users = data["props"]["users"]
        assert len(users) == 3
        assert users[0]["id"] == 1
        assert users[0]["name"] == "Alice"
        assert users[0]["email"] == "alice@example.com"
        assert "created_at" in users[0]


def test_inertia_partial_request(app):
    with TestClient(app) as client:
        response = client.get(
            "/partial-demo",
            headers={
                InertiaHeader.INERTIA: "true",
                InertiaHeader.PARTIAL_COMPONENT: "PartialDemo",
                InertiaHeader.PARTIAL_ONLY: "public_data,timestamp",
            },
        )

        assert response.status_code == 200
        data = response.json()

        props = data["props"]
        assert "flash" in props
        assert "public_data" in props
        assert "timestamp" in props
        assert "private_data" not in props
        assert "lazy_data" not in props


def test_inertia_partial_request_with_except(app):
    with TestClient(app) as client:
        response = client.get(
            "/partial-demo",
            headers={
                InertiaHeader.INERTIA: "true",
                InertiaHeader.PARTIAL_COMPONENT: "PartialDemo",
                InertiaHeader.PARTIAL_ONLY: "public_data,private_data,timestamp",
                InertiaHeader.PARTIAL_EXCEPT: "private_data",
            },
        )

        assert response.status_code == 200
        data = response.json()

        props = data["props"]
        assert "flash" in props
        assert "public_data" in props
        assert "timestamp" in props
        assert "private_data" not in props


def test_inertia_shared_props(app):
    with TestClient(app) as client:
        response = client.get("/shared-demo", headers={InertiaHeader.INERTIA: "true"})

        assert response.status_code == 200
        data = response.json()

        props = data["props"]

        assert props["flash"] == {}
        assert props["app_name"] == "Test App"
        assert props["user"]["name"] == "John"
        assert props["user"]["role"] == "admin"
        assert props["page_data"] == "Page specific data"


def test_inertia_callable_props(app):
    """Test dynamic property resolution"""

    with TestClient(app) as client:
        response = client.get("/partial-demo", headers={InertiaHeader.INERTIA: "true"})

        assert response.status_code == 200
        data = response.json()

        props = data["props"]
        assert "flash" in props
        assert isinstance(props["timestamp"], str)

        datetime.fromisoformat(props["timestamp"])


def test_inertia_user_detail_route(app):
    """Test user detail route"""

    with TestClient(app) as client:
        response = client.get("/users/123", headers={InertiaHeader.INERTIA: "true"})

        assert response.status_code == 200
        data = response.json()

        assert data["component"] == "UserDetail"
        assert "flash" in data["props"]
        user = data["props"]["user"]
        assert user["id"] == 123
        assert user["name"] == "User123"
        assert user["email"] == "user123@example.com"


def test_inertia_optional_prop_in_non_partial(app):
    """Test OptionalProp is filtered in non-partial request"""

    with TestClient(app) as client:
        response = client.get("/partial-demo", headers={InertiaHeader.INERTIA: "true"})

        data = response.json()
        props = data["props"]

        assert "flash" in props
        # OptionalProp should be filtered out in non-partial request
        assert "lazy_data" not in props


def test_inertia_optional_prop_in_partial(app):
    """Test OptionalProp is not filtered in partial request"""

    with TestClient(app) as client:
        response = client.get(
            "/partial-demo",
            headers={
                InertiaHeader.INERTIA: "true",
                InertiaHeader.PARTIAL_COMPONENT: "PartialDemo",
                InertiaHeader.PARTIAL_ONLY: "lazy_data",
            },
        )

        data = response.json()
        props = data["props"]

        assert "flash" in props
        # Specified OptionalProp should exist in partial request
        assert "lazy_data" in props
        assert props["lazy_data"] == "Lazy loaded data"


@pytest.fixture
def app_with_session() -> FastAPI:
    """FastAPI app with SessionMiddleware for flash tests"""
    app = FastAPI(title="Inertia Flash Test App")
    app.add_middleware(SessionMiddleware, secret_key="test-secret-key")

    @app.post("/create-user")
    def create_user(inertia: InertiaDepends):
        inertia.flash("success", "User created successfully")
        inertia.flash("info", "Check your email for confirmation")

        return inertia.render("CreateUser", {"user_id": 123})

    @app.post("/update-profile")
    def update_profile(inertia: InertiaDepends):
        inertia.flash("success", "Profile updated")

        return inertia.render("Profile", {"username": "john_doe"})

    @app.get("/dashboard")
    def dashboard(inertia: InertiaDepends):
        inertia.share("app_name", "Test App")

        return inertia.render("Dashboard", {"stats": {"views": 100}})

    @app.post("/error-action")
    def error_action(inertia: InertiaDepends):
        inertia.flash("error", "Operation failed")
        inertia.flash("details", {"code": 500, "message": "Internal error"})

        return inertia.render("Error", {})

    return app


def test_flash_messages_in_json_response(app_with_session):
    """Test flash messages are included in Inertia JSON response"""
    with TestClient(app_with_session) as client:
        response = client.post(
            "/create-user", headers={InertiaHeader.INERTIA: "true"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["component"] == "CreateUser"
        assert data["props"]["user_id"] == 123
        assert data["props"]["flash"]["success"] == "User created successfully"
        assert data["props"]["flash"]["info"] == "Check your email for confirmation"


def test_flash_messages_in_html_response(app_with_session):
    """Test flash messages are included in HTML response"""
    with TestClient(app_with_session) as client:
        response = client.post("/update-profile")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"

        d = pq(response.text)
        app_div = d("#app")
        page_data = json.loads(app_div.attr("data-page"))

        assert page_data["component"] == "Profile"
        assert page_data["props"]["username"] == "john_doe"
        assert page_data["props"]["flash"]["success"] == "Profile updated"


def test_flash_messages_with_shared_props(app_with_session):
    """Test flash messages work correctly with shared props"""
    with TestClient(app_with_session) as client:
        # First request to set flash messages
        client.post("/create-user", headers={InertiaHeader.INERTIA: "true"})

        # Second request to check flash messages are combined with shared props
        response = client.get("/dashboard", headers={InertiaHeader.INERTIA: "true"})

        data = response.json()
        props = data["props"]

        assert "flash" in props
        assert props["app_name"] == "Test App"
        assert props["stats"]["views"] == 100


def test_flash_supports_complex_data_types(app_with_session):
    """Test flash messages support complex data types"""
    with TestClient(app_with_session) as client:
        response = client.post(
            "/error-action", headers={InertiaHeader.INERTIA: "true"}
        )

        data = response.json()
        props = data["props"]

        assert props["flash"]["error"] == "Operation failed"
        assert props["flash"]["details"]["code"] == 500
        assert props["flash"]["details"]["message"] == "Internal error"


def test_flash_without_session_middleware():
    """Test flash raises error when SessionMiddleware is not installed"""
    app_no_session = FastAPI(title="App Without Session")

    @app_no_session.post("/action")
    def action(inertia: InertiaDepends):
        # This should raise RuntimeError
        inertia.flash("error", "This should fail")

        return inertia.render("Action", {})

    with TestClient(app_no_session, raise_server_exceptions=False) as client:
        response = client.post("/action", headers={InertiaHeader.INERTIA: "true"})

        # Should return 500 error due to missing SessionMiddleware
        assert response.status_code == 500


def test_flash_messages_cleared_after_redirect():
    """Test flash messages are cleared after being displayed following a redirect"""
    from fastapi.responses import RedirectResponse

    app = FastAPI(title="Flash Redirect Test")
    app.add_middleware(SessionMiddleware, secret_key="test-secret-key")

    @app.post("/submit")
    def submit(inertia: InertiaDepends):
        inertia.flash("success", "Form submitted successfully")

        return RedirectResponse(url="/result", status_code=303)

    @app.get("/result")
    def result(inertia: InertiaDepends):
        return inertia.render("Result", {"status": "ok"})

    with TestClient(app) as client:
        # Submit form
        response = client.post("/submit", follow_redirects=False)

        assert response.status_code == 303
        assert response.headers["location"] == "/result"

        # Follow redirect - flash message should appear here
        response = client.get("/result", headers={InertiaHeader.INERTIA: "true"})

        assert response.status_code == 200
        data = response.json()
        assert data["props"]["flash"]["success"] == "Form submitted successfully"

        # Second request - flash message should be gone
        response = client.get("/result", headers={InertiaHeader.INERTIA: "true"})

        assert response.status_code == 200
        data = response.json()
        assert "success" not in data["props"]["flash"]
        assert data["props"]["status"] == "ok"
