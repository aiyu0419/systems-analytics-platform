# Systems Analytics Platform

A learning-driven distributed data engineering platform for collecting, processing, storing, and analyzing system performance telemetry.

## 1. Project Overview

Systems Analytics Platform is an independent software engineering project exploring distributed data ingestion, stream processing, analytical storage, data visualization, and infrastructure deployment.

The platform will initially ingest benchmark results from [PowerPerf Lab](https://github.com/aiyu0419/powerperf-lab), with a longer-term goal of supporting additional data sources such as SoC simulations and synthetic telemetry generators.

### Engineering Objectives

- Design a reproducible data ingestion pipeline.
- Learn event-driven architecture with Apache Kafka.
- Process and aggregate benchmark events using Apache Spark.
- Design relational schemas and analytical queries with PostgreSQL.
- Build a performance analytics dashboard with Streamlit.
- Containerize services using Docker.
- Explore service deployment and recovery using Kubernetes.
- Evaluate reliability, correctness, throughput, and processing latency.

## 2. System Architecture (Planned)

**Data flow:**

PowerPerf Lab / Synthetic Event Generator

→ Python Ingestion Service

→ Apache Kafka

→ Apache Spark Structured Streaming

→ PostgreSQL and Parquet Storage

→ Streamlit Analytics Dashboard

**Infrastructure:**

- Docker Compose for local development.
- Kubernetes for later deployment experiments.

This architecture is a development target, not a description of currently implemented functionality.

## 3. Data Sources

### PowerPerf Lab

The initial data source provides:

- `config.json` — Benchmark configuration.
- `metadata.json` — System and runtime metadata.
- `runs.csv` — Benchmark execution results.
- `telemetry.csv` — CPU utilization and available memory samples.

The ingestion system will normalize these files into versioned events.

The current PowerPerf data does not include direct electrical power or energy measurements.

## 4. Technology Stack

| Component | Planned Technology |
| --- | --- |
| Programming language | Python |
| Event broker | Apache Kafka |
| Stream processing | Apache Spark |
| Database | PostgreSQL |
| Historical storage | Apache Parquet |
| Visualization | Streamlit |
| Containers | Docker / Docker Compose |
| Orchestration | Kubernetes |
| Testing | pytest |
| Version control | Git and GitHub |

## 5. Development Roadmap

- [ ] Phase 1 — Repository foundation, data contracts, and ingestion
- [ ] Phase 2 — Kafka ingestion, PostgreSQL persistence, and Docker Compose
- [ ] Phase 3 — Spark streaming and analytical transformations
- [ ] Phase 4 — Performance analytics dashboard
- [ ] Phase 5 — Kubernetes deployment
- [ ] Phase 6 — Reliability testing and performance evaluation

## 6. Current Development Status

**Phase 1, Step 1: Repository initialization**

Initial repository documentation and Git setup are in progress.

No production or local data pipeline has been implemented yet.

The next development task is to establish the Python project structure, development environment, and automated testing tools.

## 7. Engineering Principles

- **Correctness:** Validate input records and explicitly handle unsuccessful benchmark runs and missing values.
- **Idempotency:** Reprocessing an existing event must not create duplicate logical results.
- **Reproducibility:** Track configurations, environment metadata, and dependency versions.
- **Observability:** Measure processing latency, throughput, error rates, and service health.
- **Separation of concerns:** Keep performance measurement separate from distributed data processing.
- **Incremental development:** Implement and verify one working component at a time.

## 8. Project Scope and Limitations

This repository is an educational engineering project, not a production-deployed platform.

Kafka and Spark may introduce more operational complexity than the initial workload requires. Their benefits and costs will be evaluated through experiments.

Only synthetic data and personally owned benchmark results will be used. No proprietary company data will be included.

## 9. License

No open-source license has been selected yet.