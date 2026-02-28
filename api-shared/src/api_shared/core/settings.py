from enum import StrEnum
from typing import Annotated

from pydantic import AfterValidator, AnyHttpUrl, Field, PlainValidator, TypeAdapter
from pydantic_settings import BaseSettings, SettingsConfigDict

AnyHttpUrlAdapter = TypeAdapter(AnyHttpUrl)

CustomHttpUrlStr = Annotated[
    str,
    PlainValidator(AnyHttpUrlAdapter.validate_strings),
    AfterValidator(lambda x: str(x).rstrip("/")),
]


class Environment(StrEnum):
    """Possible environments."""

    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class OLTPLogMethod(StrEnum):
    LANGFUSE = "langfuse"
    LOGFIRE = "logfire"
    MANUAL = "manual"
    NONE = "none"


class SharedBaseSettings(BaseSettings):
    """Base settings class with common configuration shared across all services."""

    ENVIRONMENT: Environment = Field(
        default=Environment.DEV,
        description="Application environment (dev, test, prod).",
    )
    OLTP_LOG_METHOD: OLTPLogMethod = Field(
        default=OLTPLogMethod.NONE,
        description="OpenTelemetry logging method (none, manual, logfire, langfuse).",
    )
    OTLP_ENDPOINT: CustomHttpUrlStr | None = Field(
        default=None,
        description="OpenTelemetry GRPC endpoint for OTLP exporter.",
    )
    OLTP_STD_LOGGING_ENABLED: bool = Field(
        default=False,
        description="Enable standard logging integration with OpenTelemetry.",
    )
    HATCHET_WORKER_SLOTS: int = Field(
        default=100,
        ge=1,
        description="Maximum number of concurrent Hatchet workflow slots for a worker.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = SharedBaseSettings()  # type: ignore[call-arg]
