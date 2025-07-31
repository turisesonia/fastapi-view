import os
from pathlib import Path

import pytest
from fastapi.templating import Jinja2Templates

from fastapi_view.inertia.config import ViteConfig
from fastapi_view.inertia.vite import Vite


@pytest.fixture()
def templates() -> Jinja2Templates:
    templates_path = Path(os.path.abspath("tests/templates"))

    return Jinja2Templates(directory=templates_path)


@pytest.fixture
def manifest() -> dict:
    return {
        "_shared-CFzqlAKq.js": {
            "file": "assets/shared-ChJ_j-JJ.css",
            "src": "_shared-CFzqlAKq.js",
        },
        "_shared-B7PI925R.js": {
            "file": "assets/shared-B7PI925R.js",
            "name": "shared",
            "css": ["assets/shared-ChJ_j-JJ.css"],
        },
        "baz.js": {
            "file": "assets/baz-B2H3sXNv.js",
            "name": "baz",
            "src": "baz.js",
            "isDynamicEntry": True,
        },
        "views/bar.js": {
            "file": "assets/bar-gkvgaI9m.js",
            "name": "bar",
            "src": "views/bar.js",
            "isEntry": True,
            "imports": ["_shared-B7PI925R.js"],
            "dynamicImports": ["baz.js"],
        },
        "views/foo.js": {
            "file": "assets/foo-BRBmoGS9.js",
            "name": "foo",
            "src": "views/foo.js",
            "isEntry": True,
            "imports": ["_shared-B7PI925R.js"],
            "css": ["assets/foo-5UjPuW-k.css"],
        },
    }


def test_vite_config_in_dev_mode(templates: Jinja2Templates):
    config = ViteConfig(dev_mode=True)
    vite = Vite(config=config, templates=templates)

    assert config.dev_mode is True
    assert config.dev_server_url == "http://localhost:5173"
    assert config.static_url is None
    assert config.dist_uri_prefix is None

    global_env = templates.env.globals
    assert "vite_hmr_client" in global_env
    assert global_env["vite_hmr_client"] == vite.vite_hmr_client

    assert "vite_asset" in global_env
    assert global_env["vite_asset"] == vite.vite_asset


def test_vite_config_in_production_mode(templates: Jinja2Templates):
    with pytest.raises(ValueError):
        ViteConfig(dev_mode=False)


def test_vite_config_production_with_dist_uri_prefix(templates: Jinja2Templates):
    config = ViteConfig(dev_mode=False, dist_uri_prefix="/static")
    vite = Vite(config=config, templates=templates)

    assert config.dev_mode is False
    assert config.dist_uri_prefix == "/static"


def test_vite_config_production_with_static_url(templates: Jinja2Templates):
    config = ViteConfig(dev_mode=False, static_url="https://cdn.example.com")
    vite = Vite(config=config, templates=templates)

    assert config.dev_mode is False
    assert config.static_url == "https://cdn.example.com"


def test_generate_script_tag(templates: Jinja2Templates):
    config = ViteConfig(dev_mode=True)
    vite = Vite(config=config, templates=templates)

    assert (
        vite._script_tag("http://localhost")
        == '<script src="http://localhost"></script>'
    )

    assert (
        vite._script_tag(
            "http://localhost",
            {"type": "module", "async": None, "data": "test"},
        )
        == '<script src="http://localhost" type="module" async data="test"></script>'
    )


def test_generate_link_tag_with_dist_uri_prefix(templates: Jinja2Templates):
    config = ViteConfig(dev_mode=False, dist_uri_prefix="/static")
    vite = Vite(config=config, templates=templates)

    assert (
        vite._link_tag("/resources/css/app.css")
        == '<link rel="stylesheet" href="/static/resources/css/app.css" />'
    )

    assert (
        vite._link_tag("resources/css/app.css")
        == '<link rel="stylesheet" href="/static/resources/css/app.css" />'
    )


def test_generate_link_tag_with_static_url(templates: Jinja2Templates):
    config = ViteConfig(dev_mode=False, static_url="https://assets.io")
    vite = Vite(config=config, templates=templates)

    assert (
        vite._link_tag("/resources/css/app.css")
        == '<link rel="stylesheet" href="https://assets.io/resources/css/app.css" />'
    )

    assert (
        vite._link_tag("resources/css/app.css")
        == '<link rel="stylesheet" href="https://assets.io/resources/css/app.css" />'
    )


def test_dev_vite_setup(templates: Jinja2Templates):
    config = ViteConfig(dev_mode=True)
    vite = Vite(config=config, templates=templates)

    assert config.dev_server_url == "http://localhost:5173"
    assert config.dev_websocket_url == "http://localhost:5173/@vite/client"

    assert (
        vite.vite_hmr_client()
        == '<script src="http://localhost:5173/@vite/client" type="module"></script>'
    )
    assert (
        vite.vite_asset("/resources/js/app.js")
        == '<script src="http://localhost:5173/resources/js/app.js" type="module"></script>'
    )


def test_prd_vite_asset(templates: Jinja2Templates, manifest: dict):
    config = ViteConfig(dev_mode=False, dist_uri_prefix="/static")
    vite = Vite(config=config, templates=templates)
    vite._manifest = manifest

    assert vite.vite_asset("views/foo.js").split("\n") == [
        '<link rel="stylesheet" href="/static/assets/shared-ChJ_j-JJ.css" />',
        '<link rel="stylesheet" href="/static/assets/foo-5UjPuW-k.css" />',
        '<script src="/static/assets/foo-BRBmoGS9.js" type="module"></script>',
    ]


def test_vite_custom_dev_server_config(templates: Jinja2Templates):
    config = ViteConfig(
        dev_mode=True,
        dev_server_protocol="https",
        dev_server_host="custom.local",
        dev_server_port=3000,
        ws_client_path="custom/@vite/client",
    )
    vite = Vite(config=config, templates=templates)

    assert config.dev_server_url == "https://custom.local:3000"
    assert config.dev_websocket_url == "https://custom.local:3000/custom/@vite/client"

    assert (
        vite.vite_hmr_client()
        == '<script src="https://custom.local:3000/custom/@vite/client" type="module"></script>'
    )
    assert (
        vite.vite_asset("app.js")
        == '<script src="https://custom.local:3000/app.js" type="module"></script>'
    )


def test_vite_production_mode_hmr_client_empty(templates: Jinja2Templates):
    config = ViteConfig(dev_mode=False, dist_uri_prefix="/static")
    vite = Vite(config=config, templates=templates)

    assert vite.vite_hmr_client() == ""


def test_vite_asset_not_found_in_manifest(templates: Jinja2Templates, manifest: dict):
    config = ViteConfig(dev_mode=False, dist_uri_prefix="/static")
    vite = Vite(config=config, templates=templates)
    vite._manifest = manifest

    with pytest.raises(FileNotFoundError, match="Asset not found: nonexistent.js"):
        vite.vite_asset("nonexistent.js")
