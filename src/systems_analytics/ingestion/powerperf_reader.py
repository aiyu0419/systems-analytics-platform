"""Read PowerPerf experiment files into validated event models."""

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from systems_analytics.ingestion.schemas import (
    BenchmarkRunEvent,
    TelemetryEvent,
    make_event_id,
)

RUN_COLUMNS = (
    "run_id",
    "block",
    "workers",
    "iterations",
    "warmup",
    "status",
    "exit_code",
    "wall_time_s",
    "workload_time_s",
    "checksum",
    "timestamp_utc",
    "stderr",
)

TELEMETRY_COLUMNS = (
    "run_id",
    "timestamp_utc",
    "cpu_percent_system",
    "memory_available_bytes",
)


class IngestionError(ValueError):
    """Raised when an experiment file cannot be ingested."""


@dataclass(frozen=True)
class ExperimentData:
    """A validated, in-memory representation of one experiment."""

    experiment_id: str
    host_id: str
    config: dict[str, Any]
    metadata: dict[str, Any]
    runs: list[BenchmarkRunEvent]
    telemetry: list[TelemetryEvent]


def _read_json_object(path: Path) -> dict[str, Any]:
    """Read a JSON file whose top-level value must be an object."""
    try:
        with path.open(encoding="utf-8") as stream:
            data = json.load(stream)
    except (OSError, json.JSONDecodeError) as error:
        raise IngestionError(f"Cannot read {path}: {error}") from error

    if not isinstance(data, dict):
        raise IngestionError(f"{path}: expected a JSON object")

    return data


def _read_csv(
    path: Path,
    expected_columns: tuple[str, ...],
) -> list[tuple[int, dict[str, str]]]:
    """Read CSV rows and validate their column structure."""
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            found = reader.fieldnames

            if found is None:
                raise IngestionError(f"{path}: missing CSV header")

            if len(found) != len(set(found)):
                raise IngestionError(f"{path}: duplicate column names")

            missing = set(expected_columns) - set(found)
            unexpected = set(found) - set(expected_columns)

            if missing or unexpected:
                raise IngestionError(
                    f"{path}: missing={sorted(missing)}, "
                    f"unexpected={sorted(unexpected)}"
                )

            records = []
            for row in reader:
                line_number = reader.line_num

                if None in row or any(v is None for v in row.values()):
                    raise IngestionError(f"{path}:{line_number}: malformed CSV row")

                records.append((line_number, row))

            return records

    except (OSError, csv.Error) as error:
        raise IngestionError(f"Cannot read {path}: {error}") from error


def _required_int(value: str) -> int:
    """Convert a required CSV integer."""
    return int(value.strip())


def _optional_int(value: str) -> int | None:
    """Convert empty CSV cells to None."""
    if not value.strip():
        return None
    return int(value.strip())


def _required_float(value: str) -> float:
    """Convert a required CSV floating-point value."""
    return float(value.strip())


def _optional_float(value: str) -> float | None:
    """Convert an optional CSV floating-point value."""
    if not value.strip():
        return None
    return float(value.strip())


def _parse_bool(value: str) -> bool:
    """Parse explicit Boolean representations."""
    normalized = value.strip().lower()

    if normalized in {"true", "1"}:
        return True
    if normalized in {"false", "0"}:
        return False

    raise ValueError(f"Invalid Boolean value: {value!r}")


def _parse_timestamp(value: str) -> datetime:
    """Parse an ISO 8601 timestamp into a datetime."""
    normalized = value.strip().replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _run_event(
    row: dict[str, str],
    experiment_id: str,
    host_id: str,
) -> BenchmarkRunEvent:
    """Convert one PowerPerf run row into a validated event."""
    run_id = row["run_id"].strip()

    return BenchmarkRunEvent(
        experiment_id=experiment_id,
        host_id=host_id,
        event_id=make_event_id("benchmark_run", experiment_id, run_id),
        run_id=run_id,
        block=_required_int(row["block"]),
        workers=_required_int(row["workers"]),
        iterations=_required_int(row["iterations"]),
        warmup=_parse_bool(row["warmup"]),
        status=row["status"].strip(),
        exit_code=_optional_int(row["exit_code"]),
        wall_time_s=_required_float(row["wall_time_s"]),
        workload_time_s=_optional_float(row["workload_time_s"]),
        checksum=_optional_int(row["checksum"]),
        timestamp_utc=_parse_timestamp(row["timestamp_utc"]),
        stderr=row["stderr"],
    )


def _telemetry_event(
    row: dict[str, str],
    experiment_id: str,
    host_id: str,
    sample_index: int,
) -> TelemetryEvent:
    """Convert one PowerPerf telemetry row into an event."""
    run_id = row["run_id"].strip()

    return TelemetryEvent(
        experiment_id=experiment_id,
        host_id=host_id,
        run_id=run_id,
        sample_index=sample_index,
        event_id=make_event_id(
            "benchmark_telemetry",
            experiment_id,
            f"{run_id}:{sample_index}",
        ),
        timestamp_utc=_parse_timestamp(row["timestamp_utc"]),
        cpu_percent_system=_required_float(row["cpu_percent_system"]),
        memory_available_bytes=_required_int(row["memory_available_bytes"]),
    )


def read_experiment(
    directory: Path,
    *,
    experiment_id: str,
    host_id: str,
) -> ExperimentData:
    """Load and validate all four files of a PowerPerf experiment."""
    if not experiment_id.strip() or not host_id.strip():
        raise IngestionError("experiment_id and host_id must be nonempty")

    directory = Path(directory)

    config = _read_json_object(directory / "config.json")
    metadata = _read_json_object(directory / "metadata.json")

    runs: list[BenchmarkRunEvent] = []
    seen_run_ids: set[str] = set()

    for line, row in _read_csv(directory / "runs.csv", RUN_COLUMNS):
        try:
            event = _run_event(row, experiment_id, host_id)
        except (ValueError, ValidationError) as error:
            raise IngestionError(f"runs.csv:{line}: {error}") from error

        if event.run_id in seen_run_ids:
            raise IngestionError(f"runs.csv:{line}: duplicate run_id {event.run_id}")

        seen_run_ids.add(event.run_id)
        runs.append(event)

    telemetry: list[TelemetryEvent] = []
    sample_counts: dict[str, int] = defaultdict(int)

    for line, row in _read_csv(directory / "telemetry.csv", TELEMETRY_COLUMNS):
        run_id = row["run_id"].strip()

        if run_id not in seen_run_ids:
            raise IngestionError(f"telemetry.csv:{line}: unknown run_id {run_id!r}")

        sample_index = sample_counts[run_id]

        try:
            event = _telemetry_event(
                row,
                experiment_id,
                host_id,
                sample_index,
            )
        except (ValueError, ValidationError) as error:
            raise IngestionError(f"telemetry.csv:{line}: {error}") from error

        telemetry.append(event)
        sample_counts[run_id] += 1

    return ExperimentData(
        experiment_id=experiment_id,
        host_id=host_id,
        config=config,
        metadata=metadata,
        runs=runs,
        telemetry=telemetry,
    )
