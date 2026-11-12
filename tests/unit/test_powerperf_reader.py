"""Tests for PowerPerf experiment file ingestion."""

import csv
import json
from pathlib import Path

import pytest

from systems_analytics.ingestion.powerperf_reader import (
    RUN_COLUMNS,
    TELEMETRY_COLUMNS,
    IngestionError,
    read_experiment,
)


def write_csv(
    path: Path,
    columns: tuple[str, ...],
    rows: list[dict[str, str]],
) -> None:
    """Write a CSV fixture."""
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def experiment_dir(tmp_path: Path) -> Path:
    """Create a realistic, small PowerPerf experiment."""
    config = {
        "worker_counts": [1, 2, 4],
        "iterations": 8_000_000,
        "repetitions": 2,
        "warmups": 1,
    }
    metadata = {
        "machine": "arm64",
        "platform": "macOS",
        "captured_utc": "2026-11-11T15:00:00+00:00",
    }

    (tmp_path / "config.json").write_text(json.dumps(config), encoding="utf-8")
    (tmp_path / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    runs = [
        {
            "run_id": "r001",
            "block": "0",
            "workers": "4",
            "iterations": "8000000",
            "warmup": "False",
            "status": "ok",
            "exit_code": "0",
            "wall_time_s": "2.4",
            "workload_time_s": "2.3",
            "checksum": "12345",
            "timestamp_utc": "2026-11-11T15:00:00+00:00",
            "stderr": "",
        },
        {
            "run_id": "r002",
            "block": "0",
            "workers": "4",
            "iterations": "8000000",
            "warmup": "False",
            "status": "timeout",
            "exit_code": "",
            "wall_time_s": "180.0",
            "workload_time_s": "",
            "checksum": "",
            "timestamp_utc": "2026-11-11T15:01:00+00:00",
            "stderr": "timeout after 180s",
        },
    ]

    telemetry = [
        {
            "run_id": "r001",
            "timestamp_utc": "2026-11-11T15:00:00+00:00",
            "cpu_percent_system": "45.0",
            "memory_available_bytes": "100000000",
        },
        {
            "run_id": "r001",
            "timestamp_utc": "2026-11-11T15:00:01+00:00",
            "cpu_percent_system": "47.0",
            "memory_available_bytes": "90000000",
        },
        {
            "run_id": "r002",
            "timestamp_utc": "2026-11-11T15:01:00+00:00",
            "cpu_percent_system": "52.0",
            "memory_available_bytes": "80000000",
        },
    ]

    write_csv(tmp_path / "runs.csv", RUN_COLUMNS, runs)
    write_csv(
        tmp_path / "telemetry.csv",
        TELEMETRY_COLUMNS,
        telemetry,
    )
    return tmp_path


def load(directory: Path):
    """Load a fixture with consistent identifiers."""
    return read_experiment(
        directory,
        experiment_id="exp-001",
        host_id="macbook-01",
    )


def change_first_run(
    directory: Path,
    column: str,
    value: str,
) -> None:
    """Modify a single run field to test validation."""
    path = directory / "runs.csv"

    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    rows[0][column] = value
    write_csv(path, RUN_COLUMNS, rows)


def test_read_experiment(experiment_dir: Path) -> None:
    data = load(experiment_dir)

    assert data.experiment_id == "exp-001"
    assert data.config["iterations"] == 8_000_000
    assert data.metadata["machine"] == "arm64"
    assert len(data.runs) == 2
    assert len(data.telemetry) == 3


def test_csv_values_are_parsed(experiment_dir: Path) -> None:
    run = load(experiment_dir).runs[0]

    assert run.workers == 4
    assert isinstance(run.workers, int)
    assert run.warmup is False
    assert run.wall_time_s == 2.4
    assert isinstance(run.wall_time_s, float)


def test_timeout_is_preserved(experiment_dir: Path) -> None:
    timeout = load(experiment_dir).runs[1]

    assert timeout.status == "timeout"
    assert timeout.wall_time_s == 180.0
    assert timeout.workload_time_s is None
    assert timeout.checksum is None


def test_telemetry_indices(experiment_dir: Path) -> None:
    samples = load(experiment_dir).telemetry

    assert [sample.sample_index for sample in samples] == [0, 1, 0]
    assert samples[0].run_id == "r001"
    assert samples[2].run_id == "r002"


def test_event_ids_stable_on_reimport(
    experiment_dir: Path,
) -> None:
    first = load(experiment_dir)
    second = load(experiment_dir)

    assert [run.event_id for run in first.runs] == [run.event_id for run in second.runs]
    assert [sample.event_id for sample in first.telemetry] == [
        sample.event_id for sample in second.telemetry
    ]


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("workers", "four"),
        ("warmup", "maybe"),
        ("wall_time_s", "-2.0"),
        ("status", "completed"),
    ],
)
def test_invalid_run_rejected(
    experiment_dir: Path,
    column: str,
    value: str,
) -> None:
    change_first_run(experiment_dir, column, value)

    with pytest.raises(IngestionError, match="runs.csv"):
        load(experiment_dir)


def test_naive_timestamp_rejected(
    experiment_dir: Path,
) -> None:
    change_first_run(
        experiment_dir,
        "timestamp_utc",
        "2026-11-11T15:00:00",
    )

    with pytest.raises(IngestionError):
        load(experiment_dir)


def test_missing_source_file_rejected(
    experiment_dir: Path,
) -> None:
    (experiment_dir / "runs.csv").unlink()

    with pytest.raises(IngestionError):
        load(experiment_dir)


def test_invalid_json_rejected(experiment_dir: Path) -> None:
    (experiment_dir / "config.json").write_text(
        "{invalid json",
        encoding="utf-8",
    )

    with pytest.raises(IngestionError):
        load(experiment_dir)


def test_duplicate_run_id_rejected(
    experiment_dir: Path,
) -> None:
    path = experiment_dir / "runs.csv"

    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    rows.append(rows[0].copy())
    write_csv(path, RUN_COLUMNS, rows)

    with pytest.raises(IngestionError, match="duplicate run_id"):
        load(experiment_dir)


def test_orphan_telemetry_rejected(
    experiment_dir: Path,
) -> None:
    path = experiment_dir / "telemetry.csv"

    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    rows[0]["run_id"] = "unknown-run"
    write_csv(path, TELEMETRY_COLUMNS, rows)

    with pytest.raises(IngestionError, match="unknown run_id"):
        load(experiment_dir)


def test_missing_csv_column_rejected(
    experiment_dir: Path,
) -> None:
    path = experiment_dir / "runs.csv"

    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    columns = tuple(column for column in RUN_COLUMNS if column != "workload_time_s")
    # Remove the excluded column from every row dict
    trimmed_rows = [
        {k: v for k, v in row.items() if k != "workload_time_s"} for row in rows
    ]
    write_csv(path, columns, trimmed_rows)

    with pytest.raises(IngestionError, match="missing"):
        load(experiment_dir)
