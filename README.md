# fastapi-view

A jinja2 view template helping function for FastAPI.

Features:

- Simply setting and use function to return Jinja2Templates

### Installation

```shell
pip install fastapi-view
```

### Usage

- Jinja2 templates directory setup.

  ```python
  from fastapi_view import view_initialize
  from fastapi.templating import Jinja2Templates

  templtes = Jinja2Templates(directory="/your/view/file/path")

  view_initialize(templtes=templtes)
  ```

- Use `view()`

  ```python
  from fastapi import FastAPI
  from fastapi_view.middleware import ViewRequestMiddleware
  from fastapi_view import view

  app = FastAPI()
  app.add_middleware(ViewRequestMiddleware)

  @app.get("/")
  def index():
      return view("index", {"foo": "bar"})
  ```

- Use `inertia.render()`

  ```python
  from fastapi import FastAPI
  from fastapi_view.middleware import ViewRequestMiddleware
  from fastapi_view import inertia

  app = FastAPI()
  app.add_middleware(ViewRequestMiddleware)

  @app.get("/inertia/page")
  def inertia_index():
      return inertia.render("Index", props={"foo": "bar"})
  ```

### Vite support

```
```