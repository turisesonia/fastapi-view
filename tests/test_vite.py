import os

import pytest
from fastapi.templating import Jinja2Templates

from fastapi_view.vite import Vite, ViteConfig


@pytest.fixture()
def templates() -> Jinja2Templates:
    return Jinja2Templates(directory=f"{os.path.abspath('tests')}/resources/views")


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


def test_vite_config(templates):
    vite = Vite(templates)
    assert isinstance(vite.config, ViteConfig)

    global_env = templates.env.globals

    assert "vite_hmr_client" in global_env
    assert global_env["vite_hmr_client"] == vite.vite_hmr_client

    assert "vite_asset" in global_env
    assert global_env["vite_asset"] == vite.vite_asset


def test_generate_script_tag(templates):
    vite = Vite(templates)

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


def test_generate_link_tag(templates):
    vite = Vite(templates)
    assert (
        vite._link_tag("/resources/css/app.css")
        == '<link rel="stylesheet" href="/resources/css/app.css" />'
    )

    assert (
        vite._link_tag("resources/css/app.css")
        == '<link rel="stylesheet" href="/resources/css/app.css" />'
    )


def test_generate_link_tag_with_static_url(templates):
    # set static_url
    os.environ["VITE_STATIC_URL"] = "https://assets.io"
    vite = Vite(templates)

    assert (
        vite._link_tag("/resources/css/app.css")
        == '<link rel="stylesheet" href="https://assets.io/resources/css/app.css" />'
    )

    assert (
        vite._link_tag("resources/css/app.css")
        == '<link rel="stylesheet" href="https://assets.io/resources/css/app.css" />'
    )

    del os.environ["VITE_STATIC_URL"]


def test_dev_vite_setup(templates):
    os.environ["VITE_DEV_MODE"] = "True"

    vite = Vite(templates)
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

    del os.environ["VITE_DEV_MODE"]


def test_prd_vite_asset(templates, manifest):
    os.environ["VITE_DEV_MODE"] = "False"

    vite = Vite(templates)
    vite._manifest = manifest

    assert vite.vite_asset("views/foo.js").split("\n") == [
        '<link rel="stylesheet" href="/assets/shared-ChJ_j-JJ.css" />',
        '<link rel="stylesheet" href="/assets/foo-5UjPuW-k.css" />',
        '<script src="/assets/foo-BRBmoGS9.js" type="module"></script>',
    ]

    del os.environ["VITE_DEV_MODE"]
