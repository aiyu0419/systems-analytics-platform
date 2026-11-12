# Systems Analytics Platform

A learning-driven distributed data engineering platform for ingesting, validating, processing, storing, and analyzing system performance telemetry.

## 1. Project Overview

Systems Analytics Platform is an independent software engineering project exploring backend development, data engineering, distributed systems, analytics, and infrastructure deployment.

The initial data source is [PowerPerf Lab](https://github.com/aiyu0419/powerperf-lab), a Python framework for controlled CPU performance experiments.

The platform is developed incrementally through tested components, documented engineering decisions, and reproducible experiments.

### Objectives

- Build reliable Python data ingestion.
- Design and validate versioned event contracts.
- Stream events through Apache Kafka.
- Process data with Spark Structured Streaming.
- Persist analytical results in PostgreSQL.
- Visualize performance metrics using Streamlit.
- Containerize services with Docker.
- Explore service management with Kubernetes.
- Evaluate data correctness, reliability, throughput, and latency.

## 2. Planned Architecture

PowerPerf Lab / Synthetic Event Generator

→ Python File Ingestion and Validation

→ Apache Kafka

→ Apache Spark Structured Streaming

→ PostgreSQL / Parquet

→ Streamlit Dashboard

Docker Compose will support local infrastructure. Kubernetes will be introduced for later deployment exercises.

This represents the target architecture. Kafka, Spark, PostgreSQL, and Kubernetes have not been implemented yet.

## 3. Technology Stack

| Component | Technology | Status |
| --- | --- | --- |
| Programming language | Python 3.14 locally | Configured |
| Packaging | Setuptools / pyproject.toml | Configured |
| Virtual environment | venv | Configured |
| Data validation | Pydantic v2 | Implemented |
| CSV and JSON ingestion | Python standard library | Implemented |
| Unit testing | pytest | Implemented |
| Linting and formatting | Ruff | Configured |
| Event streaming | Apache Kafka | Planned |
| Stream processing | Apache Spark | Planned |
| Database | PostgreSQL | Planned |
| Historical storage | Parquet | Planned |
| Visualization | Streamlit | Planned |
| Containerization | Docker Compose | Planned |
| Orchestration | Kubernetes | Planned |

## 4. Repository Structure

```text
systems-analytics-platform/
├── README.md
├── .gitignore
├── pyproject.toml
├── src/
│   └── systems_analytics/
│       ├── __init__.py
│       └── ingestion/
│           ├── __init__.py
│           ├── schemas.py
│           └── powerperf_reader.py
└── tests/
    └── unit/
        ├── test_package.py
        ├── test_event_schemas.py
        └── test_powerperf_reader.py
```

## 5. Data Sources

PowerPerf experiments produce:

- `config.json` — Experiment configuration.
- `metadata.json` — Machine and runtime metadata.
- `runs.csv` — Individual benchmark execution records.
- `telemetry.csv` — CPU utilization and available memory samples.

The current PowerPerf telemetry does not include direct measurements of electrical power or energy consumption.

## 6. Ingestion Architecture

The ingestion reader performs the following operations:

1. Read and parse the experiment's configuration and metadata.
2. Verify CSV headers and required fields.
3. Convert text values into native Python types.
4. Construct versioned Pydantic event models.
5. Validate benchmark execution semantics.
6. Generate deterministic event identifiers.
7. Reject duplicate run IDs and orphan telemetry.
8. Return validated experiment records in memory.

### Input

A directory containing the four PowerPerf files.

### Output

An `ExperimentData` object containing:

- Experiment identifier
- Host identifier
- Experiment configuration
- Source metadata
- Validated benchmark run events
- Validated telemetry events

### Identifier Strategy

The caller supplies a stable `experiment_id` and `host_id`.

Benchmark events are identified by a hash of:

`event_type + experiment_id + run_id`

Telemetry events use:

`event_type + experiment_id + run_id + sample_index`

The telemetry sample index is assigned from the source-file row order within each run.

Re-importing unchanged files with the same identifiers produces the same event IDs.

### Validation and Missing Data

The reader distinguishes missing source columns from empty optional cells.

Optional missing measurements are represented as `None`.

Unsuccessful benchmark executions are retained if structurally valid. They are not removed simply because workload timing or checksum values are unavailable.

Filtering unsuccessful executions belongs to metric-specific analytical queries.

## 7. Development Setup

### Requirements

- Python 3.14 for the current development environment
- Git
- pip

### Clone

```bash
git clone https://github.com/aiyu0419/systems-analytics-platform.git
cd systems-analytics-platform
```

### Create and activate a virtual environment

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install -e ".[dev]"
```

### Execute tests

```bash
python -m pytest -v
```

### Validate code quality

```bash
python -m ruff check .
python -m ruff format --check .
```

## 8. Using the PowerPerf Reader

The reader imports the `read_experiment` function from:

`systems_analytics.ingestion.powerperf_reader`

Example:

```python
from pathlib import Path

from systems_analytics.ingestion.powerperf_reader import read_experiment

experiment = read_experiment(
    Path("/path/to/powerperf/results/cpu-scaling"),
    experiment_id="powerperf-cpu-001",
    host_id="macbook-01",
)

print(len(experiment.runs))
print(len(experiment.telemetry))
```

The example requires an existing PowerPerf experiment directory.

No Kafka broker or database is required to execute the reader.

## 9. Automated Testing

The test suite includes:

- Package installation smoke tests.
- Pydantic schema validation tests.
- CSV numeric and Boolean parsing tests.
- Optional-field handling tests.
- Deterministic event ID tests.
- Missing-file and malformed-JSON tests.
- Duplicate run ID detection.
- Orphan telemetry detection.
- Missing CSV column detection.
- Invalid timestamp and duration rejection.

Run ingestion tests independently:

```bash
python -m pytest tests/unit/test_powerperf_reader.py -v
```

## 10. Development Roadmap

### Phase 1 — Foundation and Ingestion

- [x] Lesson 1.1 — GitHub repository initialization.
- [x] Lesson 1.2 — Python packaging and development environment.
- [x] Lesson 1.3 — Pydantic data contracts and validation.
- [x] Lesson 1.4 — PowerPerf CSV and JSON ingestion.
- [ ] Lesson 1.5 — Event serialization and export.
- [ ] Lesson 1.6 — Ingestion integration and robustness testing.

### Phase 2 — Kafka and PostgreSQL

- [ ] Configure Kafka and PostgreSQL using Docker Compose.
- [ ] Implement a Kafka event producer.
- [ ] Implement a PostgreSQL consumer.
- [ ] Establish idempotent database writes.

### Phase 3 — Spark

- [ ] Implement streaming event transformations.
- [ ] Add windowed aggregations.
- [ ] Test checkpointing and recovery.

### Phase 4 — Analytics Dashboard

- [ ] Build the Streamlit application.
- [ ] Analyze execution performance and scaling.
- [ ] Calculate reliability and data quality metrics.
- [ ] Compare experiments and investigate regressions.

### Phase 5 — Kubernetes

- [ ] Configure a local Kubernetes development environment.
- [ ] Deploy stateless application services.
- [ ] Configure health checks and resource limits.
- [ ] Test service recovery.

### Phase 6 — Evaluation

- [ ] Measure ingestion throughput.
- [ ] Measure processing latency.
- [ ] Test duplicate and malformed events.
- [ ] Evaluate system reliability.
- [ ] Document engineering tradeoffs.

## 11. Engineering Principles

**Correctness:** Validate data before downstream processing.

**Separation of concerns:** Keep performance measurement independent from distributed analytics infrastructure.

**Data retention:** Retain unsuccessful executions for reliability analysis.

**Idempotency:** Assign stable logical event identifiers and later enforce uniqueness in persistent storage.

**Reproducibility:** Preserve experiment configuration and machine metadata.

**Observability:** Design for measurable errors, latency, throughput, and recovery behavior.

**Incremental development:** Implement and test working components before adding infrastructure complexity.

## 12. Current Limitations

- The reader loads entire experiment files into memory.
- CSV parsing supports the currently known PowerPerf schema.
- Experiment and host IDs are supplied manually.
- Telemetry identifiers depend on stable source-file ordering.
- Configuration and metadata JSON are checked for top-level object structure, but not yet validated against comprehensive schemas.
- The reader stops on the first invalid record rather than producing a complete rejection report.
- Kafka, Spark, PostgreSQL, Docker, and Kubernetes are not yet implemented.
- Database-enforced deduplication does not yet exist.

The project is an educational engineering system under active development.

Only synthetic or personally owned benchmark data will be used.

## 13. License

No open-source license has been selected yet.