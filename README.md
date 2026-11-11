# Systems Analytics Platform

A learning-driven distributed data engineering platform for ingesting, processing, storing, and analyzing system performance telemetry.

## 1. Project Overview

Systems Analytics Platform is an independent software engineering project focused on distributed systems, backend development, data engineering, analytics, and infrastructure deployment.

The initial data source is [PowerPerf Lab](https://github.com/aiyu0419/powerperf-lab), a Python-based performance benchmarking framework.

The project is developed incrementally with automated tests, documented architectural decisions, and explicit verification of each implemented component.

### Engineering Objectives

- Implement structured data ingestion in Python.
- Learn event-driven architecture with Apache Kafka.
- Process telemetry using Apache Spark Structured Streaming.
- Design PostgreSQL schemas and analytical queries.
- Build interactive dashboards with Streamlit.
- Package services using Docker.
- Learn deployment and service management with Kubernetes.
- Evaluate data correctness, reliability, throughput, and processing latency.

## 2. Planned Architecture

PowerPerf Lab / Synthetic Event Generator

→ Python Data Ingestion Service

→ Apache Kafka

→ Apache Spark Structured Streaming

→ PostgreSQL / Parquet

→ Streamlit Analytics Dashboard

Docker Compose will support local infrastructure. Kubernetes will be introduced in a later phase.

This is the target architecture; it is not yet fully implemented.

## 3. Technology Stack

| Component | Technology | Status |
| --- | --- | --- |
| Programming | Python 3.11 | Configured |
| Project packaging | Setuptools / pyproject.toml | Configured |
| Virtual environment | Python venv | Configured locally |
| Unit testing | pytest | Configured |
| Linting and formatting | Ruff | Configured |
| Event streaming | Apache Kafka | Planned |
| Distributed processing | Apache Spark | Planned |
| Relational storage | PostgreSQL | Planned |
| Historical storage | Apache Parquet | Planned |
| Analytics dashboard | Streamlit | Planned |
| Containerization | Docker Compose | Planned |
| Orchestration | Kubernetes | Planned |

## 4. Repository Structure

- `src/systems_analytics/` — Application Python package.
- `tests/unit/` — Unit and smoke tests.
- `pyproject.toml` — Packaging, dependencies, and tool configuration.
- `.gitignore` — Files excluded from version control.
- `README.md` — Project documentation.

More directories will be introduced when their corresponding services are implemented.

## 5. Development Setup

### Prerequisites

- Git
- Python 3.11
- pip
- A terminal or IDE such as VS Code

### Clone the repository

`git clone https://github.com/aiyu0419/systems-analytics-platform.git`

`cd systems-analytics-platform`

### Create and activate the virtual environment

`python3.11 -m venv .venv`

`source .venv/bin/activate`

### Install the package and development dependencies

`python -m pip install -e ".[dev]"`

The editable installation allows local Python source changes to be reflected in the installed package.

### Verify the package installation

`python -c "import systems_analytics; print(systems_analytics.__file__)"`

### Run automated tests

`python -m pytest -v`

### Run linting

`python -m ruff check .`

### Check formatting

`python -m ruff format --check .`

## 6. Data Sources

### PowerPerf Lab

The platform will initially ingest the following files:

- `config.json`: Benchmark configuration.
- `metadata.json`: System and runtime information.
- `runs.csv`: Benchmark execution records.
- `telemetry.csv`: CPU utilization and memory availability measurements.

These files will be converted into versioned data contracts during the ingestion phase.

The existing telemetry does not include direct electrical power or energy measurements.

## 7. Development Roadmap

### Phase 1 — Foundation and Ingestion

- [x] Lesson 1.1 — Initialize the GitHub repository.
- [x] Lesson 1.2 — Configure Python packaging, virtual environment, pytest, and Ruff.
- [ ] Lesson 1.3 — Design and implement the ingestion data contract.
- [ ] Lesson 1.4 — Implement PowerPerf CSV and metadata readers.
- [ ] Lesson 1.5 — Validate and serialize event records.
- [ ] Lesson 1.6 — Test ingestion behavior and error handling.

### Phase 2 — Data Infrastructure

- [ ] Configure Kafka and PostgreSQL with Docker Compose.
- [ ] Implement Kafka event publishing.
- [ ] Implement an idempotent PostgreSQL consumer.
- [ ] Test pipeline recovery and duplicate handling.

### Phase 3 — Distributed Processing

- [ ] Implement Spark Structured Streaming.
- [ ] Validate and transform events.
- [ ] Compute compatible benchmark aggregates.
- [ ] Implement recovery and checkpointing tests.

### Phase 4 — Analytics Dashboard

- [ ] Build an interactive Streamlit dashboard.
- [ ] Visualize execution time and CPU scaling.
- [ ] Analyze unsuccessful benchmark executions.
- [ ] Compare experiments and investigate regressions.

### Phase 5 — Kubernetes

- [ ] Configure local Kubernetes development.
- [ ] Deploy selected application services.
- [ ] Configure probes, resources, and recovery tests.

### Phase 6 — Evaluation

- [ ] Measure pipeline throughput.
- [ ] Measure processing latency.
- [ ] Test malformed and duplicate data.
- [ ] Document performance and reliability tradeoffs.
- [ ] Prepare an end-to-end engineering demonstration.

## 8. Current Implementation Status

**Completed:**

- Git repository initialized and published.
- Python package structure created.
- `pyproject.toml` configured with Setuptools.
- Python development environment established.
- Initial package smoke tests implemented.
- Ruff linting and formatting configured.

**Next:** Define versioned schemas for benchmark execution and telemetry events.

Kafka, Spark, databases, backend services, and Kubernetes deployment have not yet been implemented.

## 9. Engineering Principles

**Correctness:** Preserve benchmark status semantics and explicitly validate missing or malformed values.

**Idempotency:** Replaying an event should not create duplicate logical results.

**Reproducibility:** Record configurations, system metadata, and relevant dependencies.

**Observability:** Monitor pipeline errors, throughput, processing latency, and service health.

**Separation of concerns:** Keep performance measurement independent from backend data infrastructure.

**Incremental development:** Verify each component with automated tests before introducing additional complexity.

## 10. Current Limitations

- No ingestion service is implemented.
- No Kafka broker or database is configured.
- No Spark streaming application exists.
- No interactive analytics dashboard exists.
- No Kubernetes deployment exists.
- Project dependencies are constrained but are not yet fully locked for reproducible builds.

The repository is an educational engineering project under active development.

Only personally owned or synthetic benchmark data will be used. Proprietary employer data is excluded.

## 11. License

No open-source license has been selected yet.