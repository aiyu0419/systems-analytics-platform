"""Versioned data contracts for PowerPerf events."""

from datetime import datetime, timezone
from hashlib import sha256
from json import dumps
from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


def make_event_id(
    event_type: str,
    experiment_id: str,
    record_key: str,
) -> str:
    """Create a stable identifier from logical event identity."""
    canonical = dumps(
        [event_type, experiment_id, record_key],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


class EventBase(BaseModel):
    """Shared fields and validation for all PowerPerf events."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    schema_version: Literal[1] = 1
    source: Literal["powerperf"] = "powerperf"

    event_id: str = Field(min_length=1)
    experiment_id: str = Field(min_length=1)
    host_id: str = Field(min_length=1)
    timestamp_utc: datetime

    @field_validator("timestamp_utc")
    @classmethod
    def enforce_utc(cls, value: datetime) -> datetime:
        """Require a timezone and normalize the time to UTC."""
        if value.utcoffset() is None:
            raise ValueError("timestamp_utc must include timezone information")

        return value.astimezone(timezone.utc)


class BenchmarkRunEvent(EventBase):
    """A completed PowerPerf benchmark execution."""

    event_type: Literal["benchmark_run"] = "benchmark_run"

    run_id: str = Field(min_length=1)
    block: int = Field(ge=0)
    workers: int = Field(gt=0)
    iterations: int = Field(gt=0)
    warmup: bool

    status: Literal[
        "ok",
        "failed",
        "timeout",
        "error",
        "invalid_output",
    ]

    exit_code: int | None = None

    wall_time_s: float = Field(
        gt=0,
        allow_inf_nan=False,
    )

    workload_time_s: float | None = Field(
        default=None,
        ge=0,
        allow_inf_nan=False,
    )

    checksum: int | None = None
    stderr: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def check_consistency(self) -> Self:
        """Validate event identity and successful-run semantics."""
        expected = make_event_id(
            "benchmark_run",
            self.experiment_id,
            self.run_id,
        )

        if self.event_id != expected:
            raise ValueError(
                "event_id must match the deterministic benchmark run identifier"
            )

        if self.status == "ok" and self.checksum is None:
            raise ValueError("successful runs require a checksum")

        if self.status == "ok" and self.exit_code != 0:
            raise ValueError("successful runs require exit_code=0")

        return self


class TelemetryEvent(EventBase):
    """A CPU and memory sample associated with a benchmark run."""

    event_type: Literal["benchmark_telemetry"] = "benchmark_telemetry"

    run_id: str = Field(min_length=1)
    sample_index: int = Field(ge=0)

    cpu_percent_system: float = Field(
        ge=0,
        le=100,
        allow_inf_nan=False,
    )

    memory_available_bytes: int = Field(ge=0)

    @model_validator(mode="after")
    def check_consistency(self) -> Self:
        """Verify the telemetry sample identifier."""
        expected = make_event_id(
            "benchmark_telemetry",
            self.experiment_id,
            f"{self.run_id}:{self.sample_index}",
        )

        if self.event_id != expected:
            raise ValueError(
                "event_id must match the deterministic telemetry identifier"
            )

        return self
