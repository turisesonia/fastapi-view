import os
from fastapi import Request
from fastapi.templating import Jinja2Templates


class _View(object):
    def __init__(self):
        self._views_directory = f"{os.path.abspath('')}/resources/views"
        self._templates = Jinja2Templates(directory=self.views_directory)

    @property
    def views_directory(self):
        return self._views_directory

    @views_directory.setter
    def views_directory(self, views_directory: str):
        self._views_directory = views_directory
        self._templates = Jinja2Templates(directory=self.views_directory)

    def __call__(self, view_path: str, context: dict):

        if "request" not in context:
            raise ValueError('context must include a "request" key')

        if not isinstance(context["request"], Request):
            raise ValueError("request instance type must be fastapi.Request")

        if not view_path.endswith(".html"):
            view_path = f"{view_path}.html"

        return self._templates.TemplateResponse(view_path, context)
