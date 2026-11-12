# Systems Analytics Platform

A learning-driven distributed data engineering platform for collecting, validating, processing, storing, and analyzing system performance telemetry.

## 1. Project Overview

Systems Analytics Platform is an independent engineering project focused on backend software development, distributed systems, data engineering, analytics, and infrastructure deployment.

The initial data source is [PowerPerf Lab](https://github.com/aiyu0419/powerperf-lab), a Python-based framework for controlled CPU performance experiments.

The platform will evolve incrementally from a local Python ingestion application into a distributed analytics system using Kafka, Spark, PostgreSQL, Docker, and Kubernetes.

### Engineering Objectives

- Implement reliable data ingestion and validation.
- Design versioned event contracts.
- Build an event-driven architecture using Kafka.
- Implement distributed transformations with Spark.
- Design analytical storage with PostgreSQL.
- Visualize experiment performance and reliability.
- Containerize and deploy application services.
- Evaluate throughput, latency, correctness, and recovery behavior.

## 2. Planned Architecture

**Data sources**

PowerPerf Lab / Synthetic Event Generator / Future SoC Simulations

↓

**Python Ingestion Layer**

Schema validation, source normalization, deterministic event identification

↓

**Apache Kafka**

Event distribution, retention, and replay

↓

**Apache Spark Structured Streaming**

Streaming transformations and aggregation

↓

**PostgreSQL / Parquet**

Structured results and historical data

↓

**Streamlit Dashboard**

Engineering performance analytics and regression investigation

Docker Compose will provide the initial infrastructure environment. Kubernetes deployment will be introduced later.

## 3. Technology Stack

| Component | Technology | Status |
| --- | --- | --- |
| Language | Python 3.14 | Configured |
| Packaging | Setuptools / pyproject.toml | Configured |
| Virtual environment | venv | Configured |
| Schema validation | Pydantic v2 | Implemented |
| Testing | pytest | Configured |
| Linting | Ruff | Configured |
| Event broker | Kafka | Planned |
| Stream processing | Spark | Planned |
| Database | PostgreSQL | Planned |
| Historical storage | Parquet | Planned |
| Visualization | Streamlit | Planned |
| Containers | Docker Compose | Planned |
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
│           └── schemas.py
└── tests/
    └── unit/
        ├── test_package.py
        └── test_event_schemas.py
```

Additional service, storage, and deployment directories will be created during subsequent phases.

## 5. Data Sources and Event Contracts

### PowerPerf Lab

The platform will ingest four source files:

- `config.json`: Experiment parameters.
- `metadata.json`: Machine and runtime metadata.
- `runs.csv`: Benchmark execution records.
- `telemetry.csv`: CPU and memory telemetry samples.

The existing PowerPerf telemetry does not directly measure electrical power or energy consumption.

### BenchmarkRunEvent

Represents one completed benchmark execution.

Important fields include:

- `event_id`: Deterministic logical event identifier.
- `experiment_id`: Stable experiment identifier.
- `host_id`: Source machine identifier.
- `run_id`: Original PowerPerf run identifier.
- `workers`: Number of worker processes.
- `iterations`: Total workload size.
- `warmup`: Whether the run is a warmup.
- `status`: Execution outcome.
- `wall_time_s`: Controller-measured elapsed time.
- `workload_time_s`: Optional workload-reported time.
- `checksum`: Optional validated workload output.
- `timestamp_utc`: Timezone-aware timestamp.

### TelemetryEvent

Represents one system telemetry sample linked to a benchmark run.

Important fields include:

- `event_id`
- `experiment_id`
- `host_id`
- `run_id`
- `sample_index`
- `timestamp_utc`
- `cpu_percent_system`
- `memory_available_bytes`

### Event Identification

Benchmark event identity uses:

`event_type + experiment_id + run_id`

Telemetry event identity uses:

`event_type + experiment_id + run_id + sample_index`

Identifiers are generated using SHA-256 over a canonical JSON representation of their components.

The stable experiment identifier and telemetry sample ordering will be supplied by the ingestion reader in the next lesson.

### Validation Rules

- Unexpected fields are rejected.
- Required identifiers must be nonempty.
- Worker counts and iteration counts must be positive.
- Wall-clock duration must be finite and positive.
- CPU utilization must be between 0 and 100 percent.
- Memory availability cannot be negative.
- Timestamps must include timezone information and are normalized to UTC.
- Successful runs require a checksum and exit code zero.
- Failed or timed-out runs may have missing workload timing and checksum.
- An event identifier must match its declared logical identity.

### Schema Versioning

Events currently use schema version `1`.

Future incompatible changes will require explicit schema evolution rather than silently changing the interpretation of existing data.

## 6. Development Setup

### Requirements

- Python 3.14
- Git
- pip

### Clone the repository

```bash
git clone https://github.com/aiyu0419/systems-analytics-platform.git
cd systems-analytics-platform
```

### Create a virtual environment

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

### Install the application and development tools

```bash
python -m pip install -e ".[dev]"
```

### Run unit tests

```bash
python -m pytest -v
```

### Run linting and formatting checks

```bash
python -m ruff check .
python -m ruff format --check .
```

## 7. Implemented Components

### Python Project Foundation

- Installable Python package using a `src/` layout.
- Dependency and tool configuration in `pyproject.toml`.
- Virtual environment setup.
- Automated smoke tests.
- Ruff linting and formatting.

### Data Contracts

- Shared `EventBase` model.
- `BenchmarkRunEvent` validation model.
- `TelemetryEvent` validation model.
- Deterministic event identifier generation.
- Timezone-aware timestamp handling.
- Required and nullable field validation.
- Cross-field consistency rules.
- JSON serialization and deserialization.
- Unit tests for valid and invalid records.

## 8. Development Roadmap

### Phase 1 — Foundation and Ingestion

- [x] Lesson 1.1: GitHub repository initialization.
- [x] Lesson 1.2: Python development environment and tooling.
- [x] Lesson 1.3: Versioned event models and schema validation.
- [ ] Lesson 1.4: PowerPerf CSV and JSON file ingestion.
- [ ] Lesson 1.5: Event normalization and serialization.
- [ ] Lesson 1.6: Ingestion testing and error handling.

### Phase 2 — Kafka and PostgreSQL

- [ ] Configure Kafka and PostgreSQL with Docker Compose.
- [ ] Implement a Kafka producer.
- [ ] Implement a PostgreSQL consumer.
- [ ] Add idempotent persistence and duplicate-event tests.

### Phase 3 — Spark

- [ ] Implement Structured Streaming ingestion.
- [ ] Build transformations and analytical aggregations.
- [ ] Introduce checkpointing and recovery tests.

### Phase 4 — Analytics Dashboard

- [ ] Build Streamlit visualizations.
- [ ] Compare performance experiments.
- [ ] Analyze scaling, variability, and failure rates.
- [ ] Investigate performance regressions.

### Phase 5 — Kubernetes

- [ ] Configure a development Kubernetes environment.
- [ ] Deploy selected application services.
- [ ] Implement health probes and resource management.
- [ ] Test application recovery.

### Phase 6 — Reliability and Evaluation

- [ ] Measure ingestion throughput and processing latency.
- [ ] Evaluate duplicate handling and replay.
- [ ] Test service failures and recovery.
- [ ] Document system tradeoffs and experimental results.

## 9. Engineering Principles

**Data correctness:** Preserve the difference between missing measurements and unsuccessful executions.

**Idempotency:** Reprocessing an existing logical event must not create duplicate analytical results.

**Reproducibility:** Keep source experiment configurations, machine metadata, and software versions associated with measured results.

**Schema evolution:** Version contracts and validate backward compatibility when making changes.

**Observability:** Measure failures, throughput, processing latency, and resource utilization.

**Separation of concerns:** Keep benchmark execution independent of the distributed analytics platform.

**Incremental verification:** Test each component before introducing additional infrastructure.

## 10. Current Limitations

- PowerPerf CSV ingestion is not yet implemented.
- Experiment identifier assignment is not yet implemented.
- Kafka, Spark, PostgreSQL, and Kubernetes are not configured.
- Database-enforced idempotency does not yet exist.
- Tests currently validate data models rather than complete end-to-end processing.
- Dependency versions are constrained but not yet locked to a fully reproducible environment.

The project remains an educational engineering system under active development.

Only synthetic data or personally owned performance experiment results will be used.

## 11. License

No open-source license has been selected yet.