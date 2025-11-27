import pytest
from pydantic import ValidationError

from fastapi_view.vite.config import ViteSettings


def test_dist_uri_prefix_validation_rejects_empty_string():
    """Test that dist_uri_prefix validator rejects empty strings"""

    with pytest.raises(
        ValidationError, match="dist_uri_prefix must be a non-empty string"
    ):
        ViteSettings(dist_uri_prefix="")


def test_dist_uri_prefix_validation_accepts_none():
    """Test that dist_uri_prefix validator accepts None"""

    settings = ViteSettings(dev_mode=True, dist_uri_prefix=None)

    assert settings.dist_uri_prefix is None


def test_dist_uri_prefix_validation_accepts_valid_string():
    """Test that dist_uri_prefix validator accepts non-empty strings"""

    settings = ViteSettings(dist_uri_prefix="/static", static_url="http://example.com")

    assert settings.dist_uri_prefix == "/static"


def test_production_config_validation_requires_static_url_or_dist_uri_prefix():
    """Test that production mode requires either static_url or dist_uri_prefix"""

    with pytest.raises(
        ValidationError,
        match="static_url or dist_uri_prefix must be set in production mode",
    ):
        ViteSettings(dev_mode=False)


def test_production_config_validation_accepts_static_url():
    """Test that production mode accepts static_url"""

    settings = ViteSettings(dev_mode=False, static_url="http://cdn.example.com")

    assert settings.static_url == "http://cdn.example.com"
    assert settings.dist_uri_prefix is None


def test_production_config_validation_accepts_dist_uri_prefix():
    """Test that production mode accepts dist_uri_prefix"""

    settings = ViteSettings(dev_mode=False, dist_uri_prefix="/static")

    assert settings.dist_uri_prefix == "/static"
    assert settings.static_url is None


def test_production_config_validation_accepts_both():
    """Test that production mode accepts both static_url and dist_uri_prefix"""

    settings = ViteSettings(
        dev_mode=False, static_url="http://cdn.example.com", dist_uri_prefix="/static"
    )

    assert settings.static_url == "http://cdn.example.com"
    assert settings.dist_uri_prefix == "/static"


def test_dev_mode_does_not_require_static_url_or_dist_uri_prefix():
    """Test that dev mode doesn't require static_url or dist_uri_prefix"""

    settings = ViteSettings(dev_mode=True)

    assert settings.static_url is None
    assert settings.dist_uri_prefix is None


@pytest.mark.parametrize(
    "protocol, host, port, expected",
    [
        ("http", "localhost", 5173, "http://localhost:5173"),
        ("https", "example.com", 3000, "https://example.com:3000"),
        ("http", "127.0.0.1", 8080, "http://127.0.0.1:8080"),
    ],
)
def test_dev_server_url_property(protocol, host, port, expected):
    """Test dev_server_url property constructs correct URL"""

    settings = ViteSettings(
        dev_mode=True,
        dev_server_protocol=protocol,
        dev_server_host=host,
        dev_server_port=port,
    )

    assert settings.dev_server_url == expected


@pytest.mark.parametrize(
    "protocol, host, port, ws_path, expected",
    [
        (
            "http",
            "localhost",
            5173,
            "@vite/client",
            "http://localhost:5173/@vite/client",
        ),
        (
            "https",
            "example.com",
            3000,
            "custom/path",
            "https://example.com:3000/custom/path",
        ),
    ],
)
def test_dev_websocket_url_property(protocol, host, port, ws_path, expected):
    """Test dev_websocket_url property constructs correct URL"""

    settings = ViteSettings(
        dev_mode=True,
        dev_server_protocol=protocol,
        dev_server_host=host,
        dev_server_port=port,
        ws_client_path=ws_path,
    )

    assert settings.dev_websocket_url == expected
