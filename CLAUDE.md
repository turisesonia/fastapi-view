# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `fastapi-view`, a Python library that provides Jinja2 template helpers for FastAPI applications.
The project includes both basic view rendering and Inertia.js integration for building modern single-page applications with server-side routing.

## Development Commands

### Python Environment
- **Install dependencies**: `uv sync` (uses uv lock file)
- **Run tests**: `pytest` or `pytest -v` (configured in pyproject.toml)
- **Run specific test**: `pytest tests/unit/test_view.py` or `pytest tests/integration/test_inertia.py`
- **Lint code**: `ruff check` (configured for E, F, I, UP rules)
- **Format code**: `ruff format`

### Inertia Example Application
- **Navigate to example**: `cd examples/inertia`
<!-- - **Install JS dependencies**: `npm install`
- **Start development server**: `npm run dev` (runs Vite)
- **Build frontend assets**: `npm run build`
- **Run FastAPI server**: `fastapi-view-inertia` (configured as project script) -->

## Architecture

### Core Components

**Main Library (`fastapi_view/`)**:
- `view.py`: Core `View` class providing `render()` method for Jinja2 template responses
- `view_dependency()`: FastAPI dependency factory for injecting View instances

**Inertia Integration (`fastapi_view/inertia/`)**:
- `inertia.py`: `Inertia` class extending View with SPA capabilities, handles partial reloads, prop resolution
- `config.py`: Configuration for root template, assets version, and Vite integration
- `vite.py`: Vite asset manifest integration for production builds
- `props.py`: Special prop types (`OptionalProp`, `IgnoreFirstLoad`) for optimized rendering
- `enums.py`: HTTP headers used for Inertia protocol communication

### Example Application Structure
The `examples/inertia/` directory demonstrates a complete application with:
- **Backend** (`app/`): FastAPI routes organized by feature (auth, home, product)
- **Frontend** (`resources/`): Vue.js components with Inertia routing
- **Build System**: Vite configuration with Vue plugin

### Testing Structure
- `tests/unit/`: Unit tests for core functionality
- `tests/integration/`: Integration tests with FastAPI TestClient
- `tests/templates/`: HTML templates for testing view rendering

## Key Patterns

### Basic View Usage
```python
from fastapi_view import view_dependency, View

view = Depends(view_dependency("templates/"))
return view.render("template_name", {"key": "value"})
```

### Inertia Usage
```python
from fastapi_view.inertia import inertia_dependency, Inertia, InertiaConfig

inertia = Depends(inertia_dependency("templates/", config))
return inertia.render("ComponentName", {"props": data})
```

### Dependency Injection
Both `view_dependency()` and `inertia_dependency()` return FastAPI dependency functions that can be used with `Depends()`.

## Configuration

- **Python**: Requires Python 3.10+ (configured in pyproject.toml)
- **Build System**: Uses Hatchling backend
- **Testing**: pytest with custom configuration in pyproject.toml
- **Linting**: Ruff with specific rule selections and max line length of 300

## Future Development Tasks

<!-- This section tracks planned features and improvements for the fastapi-view project -->
<!-- Add new tasks here as they are identified -->

### Inertia.js Protocol Implementation Status

**Completed Features:**
- ✅ Basic Inertia request/response handling with `X-Inertia` header
- ✅ Partial reloads with `X-Inertia-Partial-Data`, `X-Inertia-Partial-Component`, `X-Inertia-Partial-Except`
- ✅ Props resolution including callable props and `IgnoreFirstLoad`
- ✅ Vite integration for asset management
- ✅ Basic page rendering with JSON/HTML responses

**Pending Features (Priority Order):**

- [ ] **1. Middleware Support**
  - **What**: Create FastAPI middleware to automatically detect Inertia requests and set appropriate response headers
  - **Why**: Eliminates need to manually check headers in every route, provides consistent behavior across the application
  - **Protocol Requirement**: Inertia protocol requires `X-Inertia: true` detection and proper JSON/HTML response switching
  - **Reference**: https://inertiajs.com/the-protocol

- [ ] **2. Asset Version Management**
  - **What**: Process `X-Inertia-Version` request header, compare with server version, return 409 Conflict with `X-Inertia-Location` when versions mismatch
  - **Why**: Ensures client-side assets stay synchronized with server changes, prevents stale asset issues
  - **Protocol Requirement**: Core protocol feature for cache busting - forces full page reload when assets change
  - **Reference**: https://inertiajs.com/asset-versioning

- [ ] **3. Redirect Handling**
  - **What**: Return `303 See Other` status for redirects after POST/PUT/PATCH, set `X-Inertia-Location` header for external redirects
  - **Why**: Maintains SPA experience during form submissions and prevents CORS issues with external redirects
  - **Protocol Requirement**: Standard redirect behavior defined in protocol for maintaining client-side routing
  - **Reference**: https://inertiajs.com/redirects

- [ ] **4. Form Validation Errors**
  - **What**: Return `422 Unprocessable Entity` with validation errors in JSON format for failed form submissions
  - **Why**: Allows client to display validation errors without full page reload, maintains form state
  - **Protocol Requirement**: Standard error handling pattern for form validation failures
  - **Reference**: https://inertiajs.com/validation

- [ ] **5. Enhanced Partial Reloads**
  - **What**: Improve handling of complex partial reload scenarios, nested components, and edge cases
  - **Why**: Optimizes performance by only updating necessary page sections
  - **Protocol Requirement**: Advanced partial reload features beyond basic implementation
  - **Reference**: https://inertiajs.com/partial-reloads

- [ ] **6. Error Page Handling**
  - **What**: Custom error components for HTTP errors (404, 500) with proper Inertia JSON responses
  - **Why**: Maintains SPA experience even during error states, provides consistent error handling
  - **Protocol Requirement**: Error responses should follow same JSON structure as normal pages
  - **Reference**: https://inertiajs.com/error-handling

- [ ] **7. File Upload Support**
  - **What**: Handle multipart/form-data requests, provide upload progress tracking
  - **Why**: Essential for modern web applications requiring file uploads within SPA experience  
  - **Protocol Requirement**: Standard form handling including file uploads
  - **Reference**: https://inertiajs.com/file-uploads

- [ ] **8. History State Management**
  - **What**: Properly manage browser history state, handle back/forward navigation
  - **Why**: Maintains proper browser navigation behavior in SPA context
  - **Protocol Requirement**: Client-side routing requires proper history state management
  - **Reference**: https://inertiajs.com/history

- [ ] **9. Testing Tools**
  - **What**: Create test utilities for simulating Inertia requests, validating responses, mocking client behavior
  - **Why**: Essential for testing Inertia applications, ensures protocol compliance
  - **Protocol Requirement**: Testing infrastructure needed to validate protocol implementation
  - **Reference**: https://inertiajs.com/testing

### Known Issues
- [ ] To be added as encountered

### Improvements
- [ ] To be added as identified