import json
from urllib.parse import urljoin

from jinja2.ext import Extension
from jinja2.environment import Environment

from .config import ViteSettings


class ViteExtension(Extension):
    """Jinja2 Extension for Vite asset management."""

    tags = {"vite_hmr_client", "vite_asset"}

    def __init__(self, environment: Environment):
        super().__init__(environment)

        self._settings = ViteSettings()
        self._manifest: dict | None = None

        environment.globals["vite_hmr_client"] = self.vite_hmr_client
        environment.globals["vite_asset"] = self.vite_asset

    def vite_hmr_client(self) -> str:
        if not self._settings.dev_mode:
            # production mode do not return HMR client.
            return ""

        return self._script_tag(
            src=self._settings.dev_websocket_url,
            attrs={"type": "module"},
        )

    def vite_asset(self, asset_path: str) -> str:
        if self._settings is None:
            raise RuntimeError("ViteExtension not configured. Call configure() first.")

        asset_path = asset_path.lstrip("/")

        if self._settings.dev_mode:
            return self._dev_mode_asset(asset_path)
        else:
            return self._prod_mode_asset(asset_path)

    def _dev_mode_asset(self, asset_path: str) -> str:
        return self._script_tag(
            src=f"{self._settings.dev_server_url}/{asset_path}",
            attrs={"type": "module"},
        )

    def _prod_mode_asset(self, asset_path: str) -> str:
        if self._manifest is None:
            self._load_manifest()

        if asset_path not in self._manifest:
            raise FileNotFoundError(f"Asset path {asset_path} not found in manifest")

        asset_tags = [tag for tag in self._css_assets_handle(asset_path, [])]

        file = self._manifest[asset_path]["file"]

        asset_tags.append(
            self._script_tag(
                src=self._get_production_url(file), attrs={"type": "module"}
            )
        )

        return "\n".join(asset_tags)

    def _load_manifest(self):
        with open(self._settings.manifest_path) as f:
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

    def _link_tag(self, file: str) -> str:
        while file.startswith("/"):
            file = file[1:]

        href = self._get_production_url(file)

        return f'<link rel="stylesheet" href="{href}" />'

    def _get_production_url(self, file: str) -> str:
        prefix = (
            self._settings.static_url
            if self._settings.static_url
            else self._settings.dist_uri_prefix
        )

        if not prefix.endswith("/"):
            prefix += "/"

        return urljoin(prefix, file)
