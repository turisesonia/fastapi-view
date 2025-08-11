import os
from pathlib import Path

APP_PATH: Path = Path(os.path.abspath(""))
DIST_PATH: Path = APP_PATH / "dist"
RESOURCES_PATH: Path = APP_PATH / "resources"
VIEWS_PATH: Path = RESOURCES_PATH / "views"

# Inertia 設定
INERTIA_ROOT_TEMPLATE = "app.html"
INERTIA_ASSETS_VERSION = "1.0.0"

# Vite 設定
VITE_DEV_MODE = False  # 設為 True 啟用開發模式
VITE_MANIFEST_PATH = APP_PATH / "dist" / ".vite" / "manifest.json"
VITE_DIST_PATH = APP_PATH / "dist"
VITE_DIST_URI_PREFIX = "/public"

# Session 設定
SESSION_SECRET_KEY = "fastapi-view-demo-secret-key-change-in-production"