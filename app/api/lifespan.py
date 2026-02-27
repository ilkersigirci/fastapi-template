from contextlib import asynccontextmanager
from typing import AsyncGenerator

from api_shared.hatchet_client import ensure_hatchet_connection
from fastapi import FastAPI

from app.core.telemetry import setup_opentelemetry, setup_prometheus, stop_opentelemetry
from app.db.utils import setup_db


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:  # pragma: no cover
    """Actions to run on application startup and shutdown."""

    app.middleware_stack = None

    await ensure_hatchet_connection()

    setup_db(app)
    setup_opentelemetry(app)
    setup_prometheus(app)
    app.middleware_stack = app.build_middleware_stack()

    yield

    await app.state.db_engine.dispose()
    stop_opentelemetry(app)
