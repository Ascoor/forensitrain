# Backend Structure

The backend is a FastAPI application organized into multiple modules:

- **main.py**: application entry point.
- **core/**: configuration, database helpers and utilities.
- **models/**: Pydantic data models used by the API.
- **schemas/**: re-exports of the models for compatibility.
- **services/**: business logic modules.
- **routers/**: API route handlers.
- **api/**: convenience wrappers for calling the API programmatically.
- **tests/**: pytest-based unit tests for the routers.
