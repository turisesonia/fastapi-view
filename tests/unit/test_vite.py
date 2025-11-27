import os
from pathlib import Path

import pytest
from fastapi.templating import Jinja2Templates

from fastapi_view.inertia.config import ViteSettings
from fastapi_view.inertia.vite import Vite


@pytest.fixture
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


@pytest.fixture
def dev_config() -> ViteSettings:
    return ViteSettings(dev_mode=True)


@pytest.fixture
def prod_config_with_dist_prefix() -> ViteSettings:
    return ViteSettings(dev_mode=False, dist_uri_prefix="/static")


@pytest.fixture
def prod_config_with_static_url() -> ViteSettings:
    return ViteSettings(dev_mode=False, static_url="https://cdn.example.com")


@pytest.fixture
def custom_dev_config() -> ViteSettings:
    return ViteSettings(
        dev_mode=True,
        dev_server_protocol="https",
        dev_server_host="custom.local",
        dev_server_port=3000,
        ws_client_path="custom/@vite/client",
    )


@pytest.fixture
def dev_vite(templates: Jinja2Templates, dev_config: ViteSettings) -> Vite:
    return Vite(templates, dev_config)


@pytest.fixture
def prod_vite_with_dist_prefix(
    templates: Jinja2Templates, prod_config_with_dist_prefix: ViteSettings
) -> Vite:
    return Vite(templates, prod_config_with_dist_prefix)


@pytest.fixture
def prod_vite_with_static_url(
    templates: Jinja2Templates, prod_config_with_static_url: ViteSettings
) -> Vite:
    return Vite(templates, prod_config_with_static_url)


@pytest.fixture
def custom_dev_vite(
    templates: Jinja2Templates, custom_dev_config: ViteSettings
) -> Vite:
    return Vite(templates, custom_dev_config)


@pytest.fixture
def prod_vite_with_manifest(prod_vite_with_dist_prefix: Vite, manifest: dict) -> Vite:
    prod_vite_with_dist_prefix._manifest = manifest
    return prod_vite_with_dist_prefix


def test_vite_config_in_dev_mode(
    templates: Jinja2Templates, dev_config: ViteSettings, dev_vite: Vite
):
    assert dev_config.dev_mode is True
    assert dev_config.dev_server_url == "http://localhost:5173"
    assert dev_config.static_url is None
    assert dev_config.dist_uri_prefix is None

    global_env = templates.env.globals
    assert "vite_hmr_client" in global_env
    assert global_env["vite_hmr_client"] == dev_vite.vite_hmr_client

    assert "vite_asset" in global_env
    assert global_env["vite_asset"] == dev_vite.vite_asset


def test_vite_config_in_production_mode():
    with pytest.raises(ValueError):
        ViteSettings(dev_mode=False)


def test_vite_config_production_with_dist_uri_prefix(
    prod_config_with_dist_prefix: ViteSettings, prod_vite_with_dist_prefix: Vite
):
    assert prod_config_with_dist_prefix.dev_mode is False
    assert prod_config_with_dist_prefix.dist_uri_prefix == "/static"


def test_vite_config_production_with_static_url(
    prod_config_with_static_url: ViteSettings, prod_vite_with_static_url: Vite
):
    assert prod_config_with_static_url.dev_mode is False
    assert prod_config_with_static_url.static_url == "https://cdn.example.com"


def test_generate_script_tag(dev_vite: Vite):
    assert (
        dev_vite._script_tag("http://localhost")
        == '<script src="http://localhost"></script>'
    )

    assert (
        dev_vite._script_tag(
            "http://localhost",
            {"type": "module", "async": None, "data": "test"},
        )
        == '<script src="http://localhost" type="module" async data="test"></script>'
    )


def test_generate_link_tag_with_dist_uri_prefix(prod_vite_with_dist_prefix: Vite):
    assert (
        prod_vite_with_dist_prefix._link_tag("/resources/css/app.css")
        == '<link rel="stylesheet" href="/static/resources/css/app.css" />'
    )

    assert (
        prod_vite_with_dist_prefix._link_tag("resources/css/app.css")
        == '<link rel="stylesheet" href="/static/resources/css/app.css" />'
    )


def test_generate_link_tag_with_static_url(prod_vite_with_static_url: Vite):
    assert (
        prod_vite_with_static_url._link_tag("/resources/css/app.css")
        == '<link rel="stylesheet" href="https://cdn.example.com/resources/css/app.css" />'
    )

    assert (
        prod_vite_with_static_url._link_tag("resources/css/app.css")
        == '<link rel="stylesheet" href="https://cdn.example.com/resources/css/app.css" />'
    )


def test_dev_vite_setup(dev_config: ViteSettings, dev_vite: Vite):
    assert dev_config.dev_server_url == "http://localhost:5173"
    assert dev_config.dev_websocket_url == "http://localhost:5173/@vite/client"

    assert (
        dev_vite.vite_hmr_client()
        == '<script src="http://localhost:5173/@vite/client" type="module"></script>'
    )
    assert (
        dev_vite.vite_asset("/resources/js/app.js")
        == '<script src="http://localhost:5173/resources/js/app.js" type="module"></script>'
    )


def test_prd_vite_asset(prod_vite_with_manifest: Vite):
    assert prod_vite_with_manifest.vite_asset("views/foo.js").split("\n") == [
        '<link rel="stylesheet" href="/static/assets/shared-ChJ_j-JJ.css" />',
        '<link rel="stylesheet" href="/static/assets/foo-5UjPuW-k.css" />',
        '<script src="/static/assets/foo-BRBmoGS9.js" type="module"></script>',
    ]


def test_vite_custom_dev_server_config(
    custom_dev_config: ViteSettings, custom_dev_vite: Vite
):
    assert custom_dev_config.dev_server_url == "https://custom.local:3000"
    assert (
        custom_dev_config.dev_websocket_url
        == "https://custom.local:3000/custom/@vite/client"
    )

    assert (
        custom_dev_vite.vite_hmr_client()
        == '<script src="https://custom.local:3000/custom/@vite/client" type="module"></script>'
    )
    assert (
        custom_dev_vite.vite_asset("app.js")
        == '<script src="https://custom.local:3000/app.js" type="module"></script>'
    )


def test_vite_production_mode_hmr_client_empty(prod_vite_with_dist_prefix: Vite):
    assert prod_vite_with_dist_prefix.vite_hmr_client() == ""


def test_vite_asset_not_found_in_manifest(prod_vite_with_manifest: Vite):
    with pytest.raises(
        FileNotFoundError, match="Asset path nonexistent.js not found in manifest"
    ):
        prod_vite_with_manifest.vite_asset("nonexistent.js")
