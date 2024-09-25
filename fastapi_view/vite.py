import json
import os
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings

from .view import view


class ViteConfig(BaseSettings):
    # development or production mode.
    dev_mode: bool = False

    # Vite dev server protocol (http / https)
    dev_server_protocol: str = "http"

    # Vite dev server hostname.
    dev_server_host: str = "localhost"

    # Vite dev server port.
    dev_server_port: int = 5173

    # Vite dev server path to hot module replacement.
    ws_client_path: str = "@vite/client"

    # Path to vite compiled assets (only used in production mode).
    assets_path: str | None = None

    # Vite static asset url
    static_url: str | None = None

    # Path to your manifest file generated by Vite.
    manifest_path: Path

    @computed_field
    def dev_server_url(self) -> str:
        return "{protocol}://{server_host}:{server_port}".format(
            protocol=self.dev_server_protocol,
            server_host=self.dev_server_host,
            server_port=self.dev_server_port,
        )

    @computed_field
    def dev_websocket_url(self) -> str:
        return "{dev_server_url}/{ws_client_path}".format(
            dev_server_url=self.dev_server_url,
            ws_client_path=self.ws_client_path,
        )


class Vite:
    def __init__(
        self,
        assets_path: str = None,
        static_url: str = None,
        manifest_path: str | Path = None,
        ws_client_path: str = "@vite/client",
        dev_server_protocol: str = "http",
        dev_server_host: str = "localhost",
        dev_server_port: int = 5173,
        dev_mode: bool = False,
    ):
        self._manifest: dict = None

        if not manifest_path:
            manifest_path = Path(os.path.abspath("dist/manifest.json"))

        self.config = ViteConfig(
            assets_path=assets_path,
            static_url=static_url,
            manifest_path=manifest_path,
            ws_client_path=ws_client_path,
            dev_server_protocol=dev_server_protocol,
            dev_server_host=dev_server_host,
            dev_server_port=dev_server_port,
            dev_mode=dev_mode,
        )

        self.initialize()

    def initialize(self):
        templates = view.get_templates()
        templates.env.globals["vite_hmr_client"] = self.vite_hmr_client
        templates.env.globals["vite_asset"] = self.vite_asset

    def vite_hmr_client(self) -> str:
        if not self.config.dev_mode:
            # production mode do not return HMR client.
            return ""

        return self._script_tag(
            src=self.config.dev_websocket_url,
            attrs={"type": "module"},
        )

    def vite_asset(self, asset_path: str):
        while asset_path.startswith("/"):
            asset_path = asset_path[1:]

        if self.config.dev_mode:
            return self._script_tag(
                src=f"{self.config.dev_server_url}/{asset_path}",
                attrs={"type": "module"},
            )

        self._load_manifest()

        asset_tags = [tag for tag in self._css_assets_handle(asset_path, [])]
        file_path = self._manifest[asset_path]["file"]
        src = (
            f"{self.config.static_url}/{file_path}"
            if self.config.static_url
            else f"/{file_path}"
        )

        asset_tags.append(self._script_tag(src=src, attrs={"type": "module"}))

        return "\n".join(asset_tags)

    def _load_manifest(self):
        if self._manifest is None:
            with open(self.config.manifest_path) as f:
                self._manifest = json.load(f)

    def _css_assets_handle(self, asset_path: str, processed: list[str]):
        stylesheet_tags = []

        entrypoint = self._manifest[asset_path]

        for import_ in entrypoint.get("imports", []):
            stylesheet_tags.extend(self._css_assets_handle(import_, processed))

        for css_path in entrypoint.get("css", []):
            if css_path not in processed:
                stylesheet_tags.append(self._link_tag(css_path))

                processed.append(css_path)

        yield from stylesheet_tags

    def _script_tag(self, src: str, attrs: dict = None) -> str:
        attrs_str = (
            "".join(
                f' {key}="{value}"' if value is not None else f" {key}"
                for key, value in attrs.items()
            )
            if isinstance(attrs, dict)
            else ""
        )

        return f'<script src="{src}"{attrs_str}></script>'

    def _link_tag(self, file_path: str) -> str:
        while file_path.startswith("/"):
            file_path = file_path[1:]

        href = (
            f"{self.config.static_url}/{file_path}"
            if self.config.static_url
            else f"/{file_path}"
        )

        return f'<link rel="stylesheet" href="{href}" />'
