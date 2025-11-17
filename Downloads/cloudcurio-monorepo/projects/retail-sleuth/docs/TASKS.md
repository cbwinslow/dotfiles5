# TASKS – Roadmap

## Phase 0 – Repo & Tooling

- [ ] Initialize git repo with base layout.
- [ ] Add `pyproject.toml` and basic dependencies.
- [ ] Add `go.mod` and Bubbletea dependencies.
- [ ] Create `docker-compose.yml` with PostgreSQL + Adminer.
- [ ] Add `Makefile` with common commands:
      - `make dev-up`, `make dev-down`, `make test`, `make lint`.

## Phase 1 – Data Model & Schema

- [ ] Define SQL schema for:
      - `retailers`
      - `items`
      - `item_prices`
      - `crawl_jobs`
- [ ] Implement initial migrations.
- [ ] Implement Pydantic/domain models mirroring schema.

## Phase 2 – Ingestion Core

- [ ] Implement `BaseClient` and `RestClient`.
- [ ] Implement `HtmlClient` wrapper around crawl4ai.
- [ ] Implement `RobotsChecker`.
- [ ] Implement `RateLimitPolicy`.
- [ ] Implement repository layer:
      - `PostgresRepository`
      - `TimeseriesRepository`

## Phase 3 – API Layer

- [ ] Implement FastAPI app with routers for retailers, items, prices.
- [ ] Add tests for endpoints (using test DB).
- [ ] Add auth (simple API token or basic auth).

## Phase 4 – TUI

- [ ] Build Bubbletea model skeleton.
- [ ] Implement dashboard + retailer list views.
- [ ] Implement item list + price history views.
- [ ] Wire TUI to FastAPI.

## Phase 5 – Recon Tooling

- [ ] Finalize Postman test script.
- [ ] Implement Node-based exporter for `discovered_endpoints`.
- [ ] Add `ApiEndpointCatalog` loader in Python.

## Phase 6 – Analytics & Infra

- [ ] Expand docker-compose to include TimescaleDB.
- [ ] Optionally add Kafka, Airflow, and Superset.
- [ ] Provide example dashboards.

## Phase 7 – Hardening

- [ ] Add structured logging and tracing.
- [ ] Add rate limit metrics.
- [ ] Add CI pipeline for tests and linting.
- [ ] Write operations and deployment docs.
