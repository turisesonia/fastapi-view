import json
from urllib.parse import urljoin

from fastapi.templating import Jinja2Templates

from .config import ViteConfig


class Vite:
    _manifest: dict = None

    def __init__(self, config: ViteConfig, templates: Jinja2Templates):
        self._config = config

        templates.env.globals["vite_hmr_client"] = self.vite_hmr_client
        templates.env.globals["vite_asset"] = self.vite_asset

    def vite_hmr_client(self) -> str:
        if not self._config.dev_mode:
            # production mode do not return HMR client.
            return ""

        return self._script_tag(
            src=self._config.dev_websocket_url,
            attrs={"type": "module"},
        )

    def vite_asset(self, asset_path: str):
        while asset_path.startswith("/"):
            asset_path = asset_path[1:]

        if self._config.dev_mode:
            return self._script_tag(
                src=f"{self._config.dev_server_url}/{asset_path}",
                attrs={"type": "module"},
            )

        self._load_manifest()

        if asset_path not in self._manifest:
            raise FileNotFoundError(f"Asset not found: {asset_path}")

        asset_tags = [tag for tag in self._css_assets_handle(asset_path, [])]

        file = self._manifest[asset_path]["file"]

        asset_tags.append(
            self._script_tag(
                src=self._get_production_url(file), attrs={"type": "module"}
            )
        )

        return "\n".join(asset_tags)

    def _load_manifest(self):
        if self._manifest is None:
            with open(self._config.manifest_path) as f:
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
            self._config.static_url
            if self._config.static_url
            else self._config.dist_uri_prefix
        )

        if not prefix.endswith("/"):
            prefix += "/"

        return urljoin(prefix, file)


# def mount(app: FastAPI):
#     if not self._config.dev_mode and not self._config.static_url:
#         route = self._config.dist_uri_prefix
#         if not route.startswith("/"):
#             route = f"/{route}"

#         app.mount(route, app=StaticFiles(directory=self._config.dist_path))
