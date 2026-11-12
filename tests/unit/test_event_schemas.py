"""Tests for benchmark and telemetry event contracts."""

import math
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from systems_analytics.ingestion.schemas import (
    BenchmarkRunEvent,
    TelemetryEvent,
    make_event_id,
)


def valid_run(**overrides: object) -> dict[str, object]:
    """Build a valid run payload, optionally overriding fields."""
    data: dict[str, object] = {
        "event_id": make_event_id("benchmark_run", "exp-001", "run-001"),
        "experiment_id": "exp-001",
        "host_id": "macbook-01",
        "run_id": "run-001",
        "timestamp_utc": datetime(2026, 11, 11, 15, 0, tzinfo=timezone.utc),
        "block": 0,
        "workers": 4,
        "iterations": 8_000_000,
        "warmup": False,
        "status": "ok",
        "exit_code": 0,
        "wall_time_s": 2.41,
        "workload_time_s": 2.32,
        "checksum": 12345,
    }
    data.update(overrides)
    return data


def valid_telemetry(**overrides: object) -> dict[str, object]:
    """Build a valid telemetry event."""
    data: dict[str, object] = {
        "event_id": make_event_id("benchmark_telemetry", "exp-001", "run-001:0"),
        "experiment_id": "exp-001",
        "host_id": "macbook-01",
        "run_id": "run-001",
        "sample_index": 0,
        "timestamp_utc": datetime(2026, 11, 11, 15, 0, tzinfo=timezone.utc),
        "cpu_percent_system": 45.0,
        "memory_available_bytes": 1_000_000,
    }
    data.update(overrides)
    return data


def test_valid_run() -> None:
    event = BenchmarkRunEvent.model_validate(valid_run())

    assert event.workers == 4
    assert event.status == "ok"
    assert event.schema_version == 1


def test_failed_run_allows_missing_checksum() -> None:
    event = BenchmarkRunEvent.model_validate(
        valid_run(
            status="failed",
            exit_code=1,
            checksum=None,
            workload_time_s=None,
        )
    )

    assert event.checksum is None
    assert event.status == "failed"


def test_success_allows_missing_workload_timing() -> None:
    event = BenchmarkRunEvent.model_validate(valid_run(workload_time_s=None))

    assert event.workload_time_s is None


def test_success_requires_checksum() -> None:
    with pytest.raises(ValidationError):
        BenchmarkRunEvent.model_validate(valid_run(checksum=None))


def test_success_requires_zero_exit_code() -> None:
    with pytest.raises(ValidationError):
        BenchmarkRunEvent.model_validate(valid_run(exit_code=1))


def test_workers_must_be_integer() -> None:
    with pytest.raises(ValidationError):
        BenchmarkRunEvent.model_validate(valid_run(workers="4"))


@pytest.mark.parametrize(
    "duration",
    [-1.0, math.nan, math.inf],
)
def test_invalid_wall_time(duration: float) -> None:
    with pytest.raises(ValidationError):
        BenchmarkRunEvent.model_validate(valid_run(wall_time_s=duration))


def test_naive_timestamp_rejected() -> None:
    with pytest.raises(ValidationError):
        BenchmarkRunEvent.model_validate(
            valid_run(timestamp_utc=datetime(2026, 11, 11, 15, 0))
        )


def test_unexpected_fields_rejected() -> None:
    with pytest.raises(ValidationError):
        BenchmarkRunEvent.model_validate(valid_run(unknown_field="unexpected"))


def test_incorrect_event_id_rejected() -> None:
    with pytest.raises(ValidationError):
        BenchmarkRunEvent.model_validate(valid_run(event_id="incorrect"))


def test_json_round_trip() -> None:
    original = BenchmarkRunEvent.model_validate(valid_run())

    serialized = original.model_dump_json()
    restored = BenchmarkRunEvent.model_validate_json(serialized)

    assert restored == original


def test_valid_telemetry() -> None:
    event = TelemetryEvent.model_validate(valid_telemetry())

    assert event.cpu_percent_system == 45.0
    assert event.memory_available_bytes == 1_000_000


def test_invalid_cpu_percent_rejected() -> None:
    with pytest.raises(ValidationError):
        TelemetryEvent.model_validate(valid_telemetry(cpu_percent_system=105.0))


def test_telemetry_ids_are_deterministic() -> None:
    first = make_event_id("benchmark_telemetry", "exp-001", "run-001:0")
    repeated = make_event_id("benchmark_telemetry", "exp-001", "run-001:0")
    next_sample = make_event_id("benchmark_telemetry", "exp-001", "run-001:1")

    assert first == repeated
    assert first != next_sample
