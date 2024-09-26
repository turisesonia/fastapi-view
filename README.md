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
  import os
  from contextlib import asynccontextmanager

  from fastapi import FastAPI
  from fastapi.staticfiles import StaticFiles
  from fastapi.templating import Jinja2Templates

  from fastapi_view import view
  from fastapi_view.middleware import ViewRequestMiddleware

  @asynccontextmanager
  async def lifespan(app: FastAPI):
      view.initialize(Jinja2Templates(directory="./assets/views"), use_vite=True)
      yield

  app = FastAPI(title="Test app", lifespan=lifespan)
  ```

- Use `view()` to render Jinja2 *.html files.

  ```python
  @app.get("/")
  def index():
      # index.html in ./assets/views
      return view("index", {"foo": "bar"})
  ```

- Use `inertia.render()` to render *.vue files.

  ```python
  from fastapi_view import inertia

  @app.get("/inertia/page")
  def inertia_index():
      # Index.vue in ./assets/js/Pages/views
      return inertia.render("Index", props={"foo": "bar"})
  ```

- Find more examples in [example](./example) directory.
