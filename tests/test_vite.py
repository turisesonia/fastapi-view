import os

import pytest
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from fastapi_view.view import view
from fastapi_view.vite import Vite, ViteConfig


@pytest.fixture(scope="module", autouse=True)
def app() -> FastAPI:
    view.initialize(
        Jinja2Templates(directory=f"{os.path.abspath('tests')}/resources/inertia")
    )


@pytest.fixture
def manifest():
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


def test_vite_config():
    vite = Vite()
    assert isinstance(vite.config, ViteConfig)

    templates = view.get_templates()
    global_env = templates.env.globals

    assert "vite_hmr_client" in global_env
    assert global_env["vite_hmr_client"] == vite.vite_hmr_client

    assert "vite_asset" in global_env
    assert global_env["vite_asset"] == vite.vite_asset


def test_generate_script_tag():
    vite = Vite()

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


def test_generate_link_tag():
    vite = Vite()
    assert (
        Vite()._link_tag("/resources/css/app.css")
        == '<link rel="stylesheet" href="/resources/css/app.css" />'
    )

    assert (
        Vite()._link_tag("resources/css/app.css")
        == '<link rel="stylesheet" href="/resources/css/app.css" />'
    )

    # set static_url
    vite = Vite(static_url="https://assets.io")
    assert (
        vite._link_tag("/resources/css/app.css")
        == '<link rel="stylesheet" href="https://assets.io/resources/css/app.css" />'
    )

    assert (
        vite._link_tag("resources/css/app.css")
        == '<link rel="stylesheet" href="https://assets.io/resources/css/app.css" />'
    )


def test_dev_vite_setup():
    vite = Vite(dev_mode=True)

    config = vite.config

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


def test_prd_vite_asset(mocker, app, manifest):
    vite = Vite(dev_mode=False)
    vite._manifest = manifest

    assert vite.vite_asset("views/foo.js").split("\n") == [
        '<link rel="stylesheet" href="/assets/shared-ChJ_j-JJ.css" />',
        '<link rel="stylesheet" href="/assets/foo-5UjPuW-k.css" />',
        '<script src="/assets/foo-BRBmoGS9.js" type="module"></script>',
    ]
