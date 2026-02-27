from functools import cache

from hatchet_sdk import Hatchet
from hatchet_sdk.opentelemetry.instrumentor import HatchetInstrumentor
from loguru import logger
from opentelemetry.trace import get_tracer_provider

from api_shared.core.settings import Environment, OLTPLogMethod, settings


@cache
def get_hatchet() -> Hatchet:
    """Return a singleton Hatchet client.

    DI wires higher-level objects (e.g., `ExternalRunner`), while this cache
    avoids re-creating the underlying Hatchet client and its connections.
    """
    hatchet = Hatchet(debug=settings.ENVIRONMENT == Environment.DEV)
    if settings.OLTP_LOG_METHOD != OLTPLogMethod.NONE:
        HatchetInstrumentor(tracer_provider=get_tracer_provider()).instrument()
    return hatchet


async def ensure_hatchet_connection() -> None:
    """Validate Hatchet connectivity for application startup."""
    if settings.ENVIRONMENT == Environment.TEST:
        return

    hatchet = get_hatchet()
    try:
        hatchet_version = await hatchet.dispatcher.get_version()
        logger.info(
            "Successfully connected to Hatchet host:{} version:{}",
            hatchet.config.host_port,
            hatchet_version,
        )
    except Exception as exc:
        details_fn = getattr(exc, "details", None)
        details = details_fn() if callable(details_fn) else None
        message = details or str(exc)
        raise ConnectionError(
            f"Failed to connect to Hatchet at {hatchet.config.host_port}: {message}"
        ) from exc


__all__ = ["ensure_hatchet_connection", "get_hatchet"]
