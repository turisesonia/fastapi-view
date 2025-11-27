import json
import os
import typing as t
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from pyquery import PyQuery as pq

from fastapi_view.inertia import Inertia, get_inertia_context
from fastapi_view.inertia.enums import InertiaHeader
from fastapi_view.inertia.props import OptionalProp

templates_path = Path(os.path.abspath("tests/templates"))


class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime = datetime.now()


# 設置環境變數以配置 templates 路徑
os.environ["FV_TEMPLATES_PATH"] = str(templates_path)
os.environ["FV_INERTIA_ROOT_TEMPLATE"] = "inertia.html"
os.environ["FV_INERTIA_ASSETS_VERSION"] = "1.0.0"
# 設置 Vite 為 dev 模式以避免需要 production 配置
os.environ["FV_VITE_DEV_MODE"] = "true"

app = FastAPI(title="Inertia Integration Test App")
InertiaDepends = t.Annotated[Inertia, Depends(get_inertia_context)]


@app.get("/")
def index(inertia: InertiaDepends, name: str = "World"):
    return inertia.render("Index", {"name": name, "message": "Welcome"})


@app.get("/users")
def users_list(inertia: InertiaDepends):
    users_data = [
        User(id=1, name="Alice", email="alice@example.com"),
        User(id=2, name="Bob", email="bob@example.com"),
        User(id=3, name="Charlie", email="charlie@example.com"),
    ]
    return inertia.render("UsersList", {"users": users_data})


@app.get("/users/{user_id}")
def user_detail(inertia: InertiaDepends, user_id: int):
    user = User(id=user_id, name=f"User{user_id}", email=f"user{user_id}@example.com")
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
    # 設定共享屬性
    Inertia.share("app_name", "Test App")
    Inertia.share("user", {"name": "John", "role": "admin"})

    return inertia.render("SharedDemo", {"page_data": "Page specific data"})


def test_inertia_html_response():
    """測試普通 HTTP 請求返回 HTML"""
    with TestClient(app) as client:
        response = client.get("/", params={"name": "Alice"})

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.template.name == "inertia.html"

        # 解析 HTML 中的 page data
        d = pq(response.text)
        app_div = d("#app")
        page_data = json.loads(app_div.attr("data-page"))

        assert page_data["component"] == "Index"
        assert page_data["props"]["name"] == "Alice"
        assert page_data["props"]["message"] == "Welcome"
        assert page_data["version"] == "1.0.0"
        assert "url" in page_data


def test_inertia_json_response():
    """測試 Inertia AJAX 請求返回 JSON"""
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
        assert data["props"]["name"] == "Bob"
        assert data["props"]["message"] == "Welcome"
        assert data["version"] == "1.0.0"
        assert "url" in data


def test_inertia_page_data_structure():
    with TestClient(app) as client:
        response = client.get("/users", headers={InertiaHeader.INERTIA: "true"})

        data = response.json()

        # 驗證基本結構
        assert "component" in data
        assert "props" in data
        assert "version" in data
        assert "url" in data

        # 驗證 Pydantic model 序列化
        users = data["props"]["users"]
        assert len(users) == 3
        assert users[0]["id"] == 1
        assert users[0]["name"] == "Alice"
        assert users[0]["email"] == "alice@example.com"
        assert "created_at" in users[0]


def test_inertia_partial_request():
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

        # 應該只包含請求的 keys
        props = data["props"]
        assert "public_data" in props
        assert "timestamp" in props
        assert "private_data" not in props
        assert "lazy_data" not in props


def test_inertia_partial_request_with_except():
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
        assert "public_data" in props
        assert "timestamp" in props
        assert "private_data" not in props


def test_inertia_shared_props():
    with TestClient(app) as client:
        response = client.get("/shared-demo", headers={InertiaHeader.INERTIA: "true"})

        assert response.status_code == 200
        data = response.json()

        props = data["props"]
        # 應該包含共享屬性和頁面特定屬性
        assert props["app_name"] == "Test App"
        assert props["user"]["name"] == "John"
        assert props["user"]["role"] == "admin"
        assert props["page_data"] == "Page specific data"


def test_inertia_callable_props():
    """測試動態屬性解析"""
    with TestClient(app) as client:
        response = client.get("/partial-demo", headers={InertiaHeader.INERTIA: "true"})

        assert response.status_code == 200
        data = response.json()

        props = data["props"]
        # timestamp 應該被解析為字串，不是 callable
        assert isinstance(props["timestamp"], str)
        # 應該是有效的 ISO 格式
        datetime.fromisoformat(props["timestamp"])


def test_inertia_user_detail_route():
    """測試用戶詳情路由"""
    with TestClient(app) as client:
        response = client.get("/users/123", headers={InertiaHeader.INERTIA: "true"})

        assert response.status_code == 200
        data = response.json()

        assert data["component"] == "UserDetail"
        user = data["props"]["user"]
        assert user["id"] == 123
        assert user["name"] == "User123"
        assert user["email"] == "user123@example.com"


def test_inertia_optional_prop_in_non_partial():
    """測試非 partial request 中 OptionalProp 被過濾"""
    with TestClient(app) as client:
        response = client.get("/partial-demo", headers={InertiaHeader.INERTIA: "true"})

        data = response.json()
        props = data["props"]

        # 非 partial request 中 OptionalProp 應該被過濾掉
        assert "lazy_data" not in props


def test_inertia_optional_prop_in_partial():
    """測試 partial request 中 OptionalProp 不被過濾"""
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

        # partial request 中指定的 OptionalProp 應該存在
        assert "lazy_data" in props
        assert props["lazy_data"] == "Lazy loaded data"
