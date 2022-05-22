import os
from fastapi import Request
from fastapi.templating import Jinja2Templates

from . import view_request


class _View(object):
    def __init__(self):
        self._views_directory = f"{os.path.abspath('')}/resources/views"
        self._templates = Jinja2Templates(directory=self.views_directory)

    @property
    def templates(self):
        return self._templates

    @property
    def views_directory(self):
        return self._views_directory

    @views_directory.setter
    def views_directory(self, views_directory: str):
        self._views_directory = views_directory
        self._templates = Jinja2Templates(directory=self.views_directory)

    def __call__(self, view_path: str, context: dict):
        request = view_request.get()

        if not request or not isinstance(request, Request):
            raise ValueError("request instance type must be fastapi.Request")

        if not view_path.endswith(".html"):
            view_path = f"{view_path}.html"

        context["request"] = request

        return self._templates.TemplateResponse(view_path, context)
