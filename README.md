# fastapi-view

A jinja2 view template helping function for FastAPI.

Features:

- Simply setting and use function to return Jinja2Templates

## Installation

```shell
pip install fastapi-view
```

# Usage

- Configuring `fastapi-view` jinja2 templates directory path

  ```python
  from fastapi_view import view

  # setting root view templates directory path
  view.views_directory = "/your/jinja2/template/directory/path"
  ```

- Use view()

  ```python
  from fastapi import FastAPI
  from fastapi.requests import Request
  from fastapi_view.middleware import ViewRequestMiddleware
  from fastapi_view import view

  app = FastAPI()

  from fastapi_view.middleware import ViewRequestMiddleware
  app.add_middleware(ViewRequestMiddleware)

  @app.get("/")
  def index():
      return view("index", {"foo": "bar"})

  ```

- Use inertia render

  ```python
  from fastapi import FastAPI
  from fastapi.requests import Request
  from fastapi_view.middleware import ViewRequestMiddleware
  from fastapi_view import inertia

  app = FastAPI()
  app.add_middleware(ViewRequestMiddleware)

  @app.get("/inertia/page")
  def inertia_index():
      return inertia.render("Index", props={"foo": "bar"})

  ```
