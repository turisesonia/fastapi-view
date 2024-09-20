from pathlib import Path

from fastapi.templating import Jinja2Templates


class ViewLoader:
    """Vite manifest loader"""

    _instance: "ViewLoader" = None

    _directory: str | Path = None

    _templates: Jinja2Templates | None = None

    def __new__(cls):
        """Singleton pattern"""

        if cls._instance is not None:
            return cls._instance

        cls._instance = super().__new__(cls)

        return cls._instance

    def set_jinja2_templates(self, directory: str | Path, **kwargs):
        self._directory = directory
        self._templates = Jinja2Templates(directory=directory, **kwargs)
