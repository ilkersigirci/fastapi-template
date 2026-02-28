from importlib import import_module

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_NAME,
    TELEMETRY_SDK_LANGUAGE,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from api_shared.core.settings import OLTPLogMethod
from api_shared.utils.general import is_module_installed


def _get_logfire_or_raise():
    if not is_module_installed("logfire"):  # pragma: no cover
        raise RuntimeError(
            "OLTP_LOG_METHOD=logfire requires optional dependency 'logfire'. "
            "Install dependency with `api-shared[logfire]`."
        )

    return import_module("logfire")


def _configure_langfuse_or_raise() -> None:
    if not is_module_installed("langfuse"):  # pragma: no cover
        raise RuntimeError(
            "OLTP_LOG_METHOD=langfuse requires optional dependency 'langfuse'. "
            "Install extras with `uv sync --extra langfuse`."
        )

    import_module("langfuse").Langfuse()


def setup_opentelemetry_worker(settings):
    """Setup OpenTelemetry instrumentation for worker."""
    if settings.OLTP_LOG_METHOD == OLTPLogMethod.NONE:
        return

    if settings.OLTP_LOG_METHOD == OLTPLogMethod.LOGFIRE:
        logfire = _get_logfire_or_raise()
        logfire.configure(environment=settings.ENVIRONMENT.value)
        logfire.instrument_system_metrics()
        logfire.instrument_httpx()

        # FIXME: Breaks the loguru logger format. Fix this
        # if settings.OLTP_STD_LOGGING_ENABLED is True:
        #     logger.configure(handlers=[logfire.loguru_handler()])

        return

    if settings.OLTP_LOG_METHOD == OLTPLogMethod.LANGFUSE:
        _configure_langfuse_or_raise()
        if settings.OLTP_STD_LOGGING_ENABLED is True:
            LoggingInstrumentor().instrument(
                tracer_provider=trace.get_tracer_provider()
            )
        return

    resource = Resource(
        attributes={
            SERVICE_NAME: getattr(settings, "PROJECT_NAME", "fastapi-template-worker"),
            TELEMETRY_SDK_LANGUAGE: "python",
            DEPLOYMENT_ENVIRONMENT: settings.ENVIRONMENT,
        },
    )
    trace_provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT, insecure=True)
    trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    if settings.OLTP_STD_LOGGING_ENABLED is True:
        LoggingInstrumentor().instrument(tracer_provider=trace_provider)
    trace.set_tracer_provider(trace_provider)


# TODO: Does this need in the worker?
def stop_opentelemetry(settings) -> None:  # pragma: no cover
    """Disables opentelemetry instrumentation."""
    if settings.OLTP_LOG_METHOD in [OLTPLogMethod.NONE, OLTPLogMethod.LOGFIRE]:
        return
