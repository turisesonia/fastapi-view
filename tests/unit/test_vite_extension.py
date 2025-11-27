import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
from jinja2 import Environment

from fastapi_view.vite.extension import ViteExtension


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
def mock_env():
    env = Mock(spec=Environment)
    env.globals = {}

    return env


@pytest.fixture
def dev_extension(mock_env, monkeypatch):
    """Create ViteExtension in dev mode"""

    monkeypatch.setenv("FV_VITE_DEV_MODE", "true")

    return ViteExtension(mock_env)


@pytest.fixture
def prod_extension(mock_env, manifest, monkeypatch):
    """Create ViteExtension in production mode with manifest"""

    with tempfile.TemporaryDirectory() as tmpdir:
        manifest_path = Path(tmpdir) / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))

        monkeypatch.setenv("FV_VITE_DEV_MODE", "false")
        monkeypatch.setenv("FV_VITE_STATIC_URL", "https://cdn.example.com")
        monkeypatch.setenv("FV_VITE_MANIFEST_PATH", str(manifest_path))

        yield ViteExtension(mock_env)


def test_vite_extension_registers_globals(mock_env, monkeypatch):
    """Test that ViteExtension registers global functions"""

    monkeypatch.setenv("FV_VITE_DEV_MODE", "true")

    ViteExtension(mock_env)

    assert "vite_hmr_client" in mock_env.globals
    assert "vite_asset" in mock_env.globals


def test_vite_hmr_client_returns_script_tag_in_dev_mode(dev_extension):
    """Test vite_hmr_client returns HMR script tag in dev mode"""

    result = dev_extension.vite_hmr_client()

    assert '<script src="http://localhost:5173/@vite/client"' in result
    assert 'type="module"' in result


def test_vite_hmr_client_returns_empty_string_in_production(prod_extension):
    """Test vite_hmr_client returns empty string in production mode"""

    result = prod_extension.vite_hmr_client()

    assert result == ""


def test_vite_asset_in_dev_mode_returns_dev_server_url(dev_extension):
    """Test vite_asset returns dev server URL in dev mode"""

    result = dev_extension.vite_asset("src/main.js")

    assert '<script src="http://localhost:5173/src/main.js"' in result
    assert 'type="module"' in result


def test_vite_asset_strips_leading_slash(dev_extension):
    """Test vite_asset strips leading slash from asset path"""

    result = dev_extension.vite_asset("/src/main.js")

    assert '<script src="http://localhost:5173/src/main.js"' in result


def test_vite_asset_in_production_mode_returns_manifest_assets(prod_extension):
    """Test vite_asset returns assets from manifest in production mode"""

    result = prod_extension.vite_asset("views/foo.js")

    assert "assets/foo-BRBmoGS9.js" in result
    assert "assets/shared-ChJ_j-JJ.css" in result
    assert "assets/foo-5UjPuW-k.css" in result
    assert 'type="module"' in result
    assert 'rel="stylesheet"' in result


def test_vite_asset_raises_error_for_missing_asset(prod_extension):
    """Test vite_asset raises FileNotFoundError for missing asset"""

    with pytest.raises(FileNotFoundError, match="Asset path .* not found in manifest"):
        prod_extension.vite_asset("non-existent.js")


def test_script_tag_with_attributes(dev_extension):
    """Test _script_tag generates correct script tag with attributes"""

    result = dev_extension._script_tag(
        "https://example.com/script.js", attrs={"type": "module", "async": None}
    )

    assert (
        result
        == '<script src="https://example.com/script.js" type="module" async></script>'
    )


def test_script_tag_without_attributes(dev_extension):
    """Test _script_tag generates correct script tag without attributes"""

    result = dev_extension._script_tag("https://example.com/script.js")

    assert result == '<script src="https://example.com/script.js"></script>'


def test_link_tag_strips_leading_slashes(prod_extension):
    """Test _link_tag strips leading slashes from file path"""

    result = prod_extension._link_tag("///assets/style.css")

    assert 'href="https://cdn.example.com/assets/style.css"' in result
    assert 'rel="stylesheet"' in result


def test_get_production_url_with_static_url(prod_extension):
    """Test _get_production_url uses static_url when available"""

    result = prod_extension._get_production_url("assets/app.js")

    assert result == "https://cdn.example.com/assets/app.js"


def test_get_production_url_adds_trailing_slash(monkeypatch, mock_env):
    """Test _get_production_url adds trailing slash to prefix"""

    monkeypatch.setenv("FV_VITE_DEV_MODE", "false")
    monkeypatch.setenv("FV_VITE_STATIC_URL", "https://cdn.example.com")

    extension = ViteExtension(mock_env)
    result = extension._get_production_url("assets/app.js")

    assert result == "https://cdn.example.com/assets/app.js"


def test_get_production_url_with_dist_uri_prefix(monkeypatch, mock_env):
    """Test _get_production_url uses dist_uri_prefix when static_url not set"""

    monkeypatch.setenv("FV_VITE_DEV_MODE", "false")
    monkeypatch.setenv("FV_VITE_DIST_URI_PREFIX", "/static")

    extension = ViteExtension(mock_env)
    result = extension._get_production_url("assets/app.js")

    assert result == "/static/assets/app.js"


def test_css_assets_handle_processes_imports_recursively(prod_extension):
    """Test _css_assets_handle processes CSS from imports recursively"""

    prod_extension._load_manifest()
    processed = []
    result = list(prod_extension._css_assets_handle("views/bar.js", processed))

    assert len(result) == 1
    assert "assets/shared-ChJ_j-JJ.css" in result[0]
    assert "assets/shared-ChJ_j-JJ.css" in processed


def test_css_assets_handle_avoids_duplicate_css(prod_extension):
    """Test _css_assets_handle doesn't duplicate already processed CSS"""

    prod_extension._load_manifest()
    processed = ["assets/shared-ChJ_j-JJ.css"]
    result = list(prod_extension._css_assets_handle("views/bar.js", processed))

    assert len(result) == 0


def test_css_assets_handle_processes_entry_css(prod_extension):
    """Test _css_assets_handle processes CSS from entry point"""

    prod_extension._load_manifest()
    processed = []
    result = list(prod_extension._css_assets_handle("views/foo.js", processed))

    assert len(result) == 2
    assert any("assets/shared-ChJ_j-JJ.css" in tag for tag in result)
    assert any("assets/foo-5UjPuW-k.css" in tag for tag in result)
