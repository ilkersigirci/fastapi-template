# Project Structure

This document explains the structure of the API template project.

## Directory Structure

```
fastapi-template/
├── app/                      # Main application package
│   ├── api/                  # API endpoints and routers
│   │   └── v1/              # API version 1
│   │       ├── endpoints/   # API endpoint modules
│   │       └── api.py       # API router assembly
│   ├── core/                # Core functionality
│   │   ├── config.py        # Application configuration
│   │   └── security.py      # Security utilities (JWT, password hashing)
│   ├── dependencies/        # FastAPI dependencies
│   │   ├── auth.py          # Authentication dependencies
│   │   └── repositories.py  # Repository and service dependencies
│   ├── models/              # Pydantic models (schemas)
│   │   ├── item.py          # Item model definitions
│   │   ├── token.py         # Token model definitions
│   │   └── user.py          # User model definitions
│   ├── repositories/        # Data access layer
│   │   ├── base.py          # Base repository interface
│   │   ├── item_repository.py  # Item data access
│   │   └── user_repository.py  # User data access
│   ├── services/            # Business logic layer
│   │   ├── item_service.py  # Item business logic
│   │   └── user_service.py  # User business logic
│   ├── utils/               # Utility functions
│   └── main.py              # Application entry point
├── docker/                  # Docker related files
├── docs/                    # Documentation
├── tests/                   # Test suite
│   ├── api/                 # API endpoint tests
│   ├── test_core/           # Core functionality tests
│   └── test_utils/          # Utility function tests
├── .env                     # Environment variables (development only)
├── .env.example             # Example environment variables template
├── pyproject.toml           # Python project configuration
└── Makefile                 # Convenience commands
```

## Architectural Layers

The project follows a multi-layered architecture:

1. **API Layer** (`app/api/`):
   - Handles HTTP requests and responses
   - Defines API endpoints and routes
   - Depends on the service layer

2. **Service Layer** (`app/services/`):
   - Implements business logic
   - Coordinates activities between multiple repositories
   - Handles exceptions and error responses
   - Depends on the repository layer

3. **Repository Layer** (`app/repositories/`):
   - Provides data access abstraction
   - Implements CRUD operations
   - Currently uses in-memory storage (can be replaced with database)

4. **Model Layer** (`app/models/`):
   - Defines data structures using Pydantic
   - Handles validation and serialization/deserialization

## Dependency Injection

The project utilizes FastAPI's dependency injection system:

- Dependencies are defined in `app/dependencies/`
- Repository and service instances are provided through dependency injection
- Authentication and authorization are implemented as dependencies

## Configuration

Application configuration is managed through:

- Environment variables (loaded from `.env` file)
- Settings class in `app/core/config.py`

## Testing

The project includes a comprehensive test suite:

- API endpoint tests in `tests/api/`
- Core functionality tests in `tests/test_core/`
- Utility function tests in `tests/test_utils/`

## Development Tools

The project provides several development tools:

- `Makefile` for common commands
- Docker configuration for containerization
- Pre-commit hooks for code quality checks
