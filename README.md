# fastapi-view

A lightweight, flexible Jinja2 template rendering library for FastAPI applications, with built-in support for Inertia.js and Vite integration.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.70%2B-009688.svg)](https://fastapi.tiangolo.com/) [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- **Simple View Rendering**: Minimal boilerplate for rendering Jinja2 templates in FastAPI routes
- **Inertia.js Support**: FastAPI Inertia.js adapter for building modern monolithic applications
- **Vite Integration**: Seamless Vite asset management with HMR support in development
- **Flexible Configuration**: Environment-based settings using Pydantic

## Installation

```bash
pip install fastapi-view
```

Or using uv:

```bash
uv add fastapi-view
```

## Quick Start

### Basic View Rendering

```python
from fastapi import FastAPI
from fastapi_view import ViewDepends

app = FastAPI()

@app.get("/")
def index(view: ViewDepends):
    return view.render("index", {"message": "Hello World"})
```

Set the templates directory via environment variable:

```bash
export FV_TEMPLATES_PATH=templates
```

### Inertia.js Integration

```python
from fastapi import FastAPI
from fastapi_view.inertia import InertiaDepends

app = FastAPI()

@app.get("/dashboard")
def dashboard(inertia: InertiaDepends):
    return inertia.render("Dashboard/Index", props={
        "user": {"name": "John Doe", "email": "john@example.com"}
    })
```

Configure Inertia via environment variables:

```bash
export FV_INERTIA_ROOT_TEMPLATE=app.html
export FV_INERTIA_ASSETS_VERSION=v1
```

### Vite Asset Management

In your Jinja2 template:

```html
<!DOCTYPE html>
<html>
  <head>
    {{ vite_hmr_client() | safe }}
    {{ vite_asset('resources/js/app.ts') | safe }}
  </head>
  <body>
    <div id="app"></div>
  </body>
</html>
```

Configure Vite settings:

```bash
export FV_VITE_DEV_MODE=true
export FV_VITE_DEV_SERVER_URL=http://localhost:5173
export FV_VITE_MANIFEST_PATH=public/build/manifest.json
```

## Configuration

`fastapi-view` uses Pydantic settings for configuration. All settings can be configured via environment variables with the `FV_` prefix.

### View Settings

| Environment Variable | Description                        | Required | Default |
| -------------------- | ---------------------------------- | -------- | ------- |
| `FV_TEMPLATES_PATH`  | Path to Jinja2 templates directory | Yes      | -       |

### Inertia Settings

| Environment Variable        | Description                         | Required | Default    |
| --------------------------- | ----------------------------------- | -------- | ---------- |
| `FV_INERTIA_ROOT_TEMPLATE`  | Root template for Inertia responses | No       | `app.html` |
| `FV_INERTIA_ASSETS_VERSION` | Asset versioning for cache busting  | No       | `None`     |

### Vite Settings

| Environment Variable          | Description                                            | Required                 | Default                    |
| ----------------------------- | ------------------------------------------------------ | ------------------------ | -------------------------- |
| `FV_VITE_DEV_MODE`            | Enable development mode with HMR                       | No                       | `False`                    |
| `FV_VITE_DEV_SERVER_PROTOCOL` | Protocol for Vite dev server (http/https)              | No                       | `http`                     |
| `FV_VITE_DEV_SERVER_HOST`     | Host for Vite dev server                               | No                       | `localhost`                |
| `FV_VITE_DEV_SERVER_PORT`     | Port for Vite dev server                               | No                       | `5173`                     |
| `FV_VITE_WS_CLIENT_PATH`      | WebSocket client path for HMR                          | No                       | `@vite/client`             |
| `FV_VITE_MANIFEST_PATH`       | Path to Vite manifest file                             | No                       | `dist/.vite/manifest.json` |
| `FV_VITE_DIST_PATH`           | Path to build output directory                         | No                       | `dist`                     |
| `FV_VITE_DIST_URI_PREFIX`     | URI prefix for serving static assets                   | Yes (in production mode) | `None`                     |
| `FV_VITE_STATIC_URL`          | Base URL for static assets (alternative to uri prefix) | Yes (in production mode) | `None`                     |

**Note**: In production mode (`FV_VITE_DEV_MODE=False`), either `FV_VITE_STATIC_URL` or `FV_VITE_DIST_URI_PREFIX` must be configured.

## Advanced Usage

### Shared Inertia Props

Share data across all Inertia responses:

```python
from fastapi import FastAPI
from fastapi_view.inertia import Inertia

app = FastAPI()

@app.on_event("startup")
def configure_inertia():
    Inertia.share("app_name", "My Application")
    Inertia.share("version", "1.0.0")
```

### Optional Props

Use optional props for lazy loading data:

```python
@app.get("/users")
def users(inertia: InertiaDepends):
    return inertia.render("Users/Index", props={
        "users": lambda: fetch_users(),  # Always evaluated
        "metrics": inertia.optional(lambda: fetch_metrics())  # Only on partial reload
    })
```

### Flash Messages

Flash messages for one-time notifications (requires SessionMiddleware):

```python
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

@app.post("/login")
def login(inertia: InertiaDepends):
    # ... authentication logic ...
    inertia.flash("success", "Login successful!")
    return inertia.render("Dashboard")
```

Flash messages are available on the frontend under the `flash` prop:

```vue
<script setup>
import { usePage } from '@inertiajs/vue3'

const page = usePage()
const flash = page.props.flash

// Access flash messages
if (flash.success) {
  console.log(flash.success)
}
if (flash.error) {
  console.log(flash.error)
}
</script>
```

### Custom Response Configuration

```python
@app.get("/custom")
def custom_view(view: ViewDepends):
    return view.render(
        "custom",
        context={"data": "value"},
        status_code=201,
        headers={"X-Custom-Header": "value"}
    )
```

## Complete Example

Check out the full Inertia.js example application in the [examples/inertia](./examples/inertia) directory, which demonstrates:

- User authentication flow
- CRUD operations with Inertia
- Vite + Vue 3 + TypeScript frontend
- Session management
- Form handling

To run the example:

```bash
cd examples/inertia
cp .env.example .env
uv sync
bun install
bun run build
uv run uvicorn app.main:app --reload
```

## Development

### Setup

```bash
git clone https://github.com/turisesonia/fastapi-view.git
cd fastapi-view
uv sync
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uvx ruff format
uvx ruff check --fix
```

## Requirements

- Python 3.10+
- FastAPI 0.70+
- Jinja2 3.0+
- Pydantic Settings 2.0+

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/turisesonia/fastapi-view)
- [Issue Tracker](https://github.com/turisesonia/fastapi-view/issues)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Inertia.js Documentation](https://inertiajs.com/)

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Template rendering powered by [Jinja2](https://jinja.palletsprojects.com/)
- Inspired by [Laravel's view system](https://laravel.com/docs/views) and [Inertia.js](https://inertiajs.com/)
